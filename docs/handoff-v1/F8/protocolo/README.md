# F8 — Procedimento do orquestrador

Quem orquestra é a sessão principal (DESENHO Q1). Não escreve no engagement, não compõe respostas nem achados: lança, releia literalmente, mede e guarda. Uma sessão nova continua por este ficheiro, pelo cartão da execução e pelo run-log.

Ferramenta: `python docs/handoff-v1/F8/tools/f8.py …` (abaixo `f8`). Pastas: cartões em `../cartoes/`, fichas do cliente em `../fichas/`, mudanças em `../mudancas/`, evidência em `../execucoes/<run>/`. Pastas neutras (fora do repositório, recriáveis a partir das fixtures): `<scratch>/f8/entregas/<run>/` e `<scratch>/f8/pacotes/<run>-r<NNNN>/`.

## 0. Antes da execução

1. O cartão `../cartoes/<run>.json` existe e aponta ficha, fontes, ponto de interrupção e mudança. `projects/<slug>` não existe.
2. Entrega inicial: copiar as fontes da fixture para `<scratch>/f8/entregas/<run>/inicial/` (só as fontes, nunca `scenario.json`).
3. `f8 runlog add --run <run> --type note --data '{"cartao": "...", "codigo": "<git sha>"}'`.
4. Cliente: lançar um subagente `general-purpose` com [CLIENTE.md](CLIENTE.md) preenchido. Guardar o `agentId` no run-log (`note`). O cliente é continuado por `SendMessage` durante toda a execução.

## 1. Segmento

1. `f8 runlog add --type segment_start --segment <S>`.
2. Lançar o executor: subagente `general-purpose`, **novo**, com [EXECUTOR.md](EXECUTOR.md) preenchido (objectivo do segmento no cartão). Em primeiro plano, salvo interrupção dura (segundo plano, para `TaskStop`).
3. A primeira mensagem do executor é `RETOMA F8`. Guardar o JSON em `../execucoes/<run>/retoma-<S>.json`; `f8 check-resume --truth ../execucoes/<run>/truth-<S anterior>.json --report …` (não há verdade anterior no S1); `f8 runlog add --type resume_check --data '<veredicto e achados>'`. Responder `CONTINUA F8`.
4. Ciclo de relé até `FIM DE SEGMENTO F8`:
   - `PEDIDO F8 tipo: pergunta` → `runlog relay_request` (texto literal, `kind: pergunta`) → `SendMessage` ao cliente com o texto literal → `runlog relay_response` (resposta literal) → `SendMessage` ao executor: `RESPOSTA F8` + resposta literal.
   - `PEDIDO F8 tipo: subagente` → `runlog relay_request` (`kind: subagente`, `subagent_type`, prompt literal) → lançar esse subagente com esse prompt, sem acrescentar nada → `runlog usage` (papel `revisor`) + `relay_response` (resultado literal) → `SendMessage` ao executor: `RESPOSTA F8` + resultado literal.
   - Um pedido mal formado volta ao executor com a razão; nunca se completa por ele.
5. Depois de cada chamada de agente, `runlog usage` com o que o harness reportar (tokens, usos de ferramenta, duração).
6. `FIM DE SEGMENTO F8` → guardar o relato em `../execucoes/<run>/fim-<S>.md`; `f8 runlog add --type segment_end`; `f8 truth --engagement <slug> --out ../execucoes/<run>/truth-<S>.json`; `f8 snapshot save --run <run> --label <S>-fim --engagement <slug>`; commit e push.

## 2. Interrupção (uma por execução, no ponto do cartão)

- **Cooperativa**: o executor devolve `PAUSA F8` no ponto combinado. `runlog interruption`; `f8 truth` → `truth-<S>-pausa.json`; `snapshot save <S>-pausa`. O executor é **descartado** — nunca mais é continuado. Um executor novo retoma o mesmo segmento (volta ao passo 1.3, contra a verdade da pausa).
- **Dura**: executor em segundo plano; `TaskStop` no momento do cartão. O resto igual.

## 3. Mudança (depois do S3)

1. Copiar a fonte de mudança de `../mudancas/<fixture>/` para `<scratch>/f8/entregas/<run>/mudanca/`; `runlog change_injected`.
2. Segmento `SM` com um executor novo: o objectivo diz que o cliente entregou a fonte nova nessa pasta.

## 4. Release, destinatário, correcção

1. Depois do S4 (release construído): copiar `projects/<slug>/_release/r<NNNN>/` para `<scratch>/f8/pacotes/<run>-r<NNNN>/`.
2. Destinatário: subagente `general-purpose` novo com [DESTINATARIO.md](DESTINATARIO.md). Guardar o relatório em `../execucoes/<run>/destinatario-1.md`; `runlog recipient` com as contagens por classe e `essential_unanswered` (lacunas `blocks_all`/`blocks_scope` que o destinatário marca como defeito, mais as perguntas bloqueantes — contadas do relatório, sem reclassificar).
3. Segmento `SC` (correcção): executor novo; o objectivo leva o relatório do destinatário, literal. Termina com um release novo.
4. Segunda leitura: destinatário novo sobre o release novo → `destinatario-2.md`; `runlog recipient` (`reading: 2`).

## 5. Avaliação

1. `f8 canary --engagement <slug> --fixture <fx> [--expected-extra ../mudancas/<fx>/expected.json] --allowed ../fichas/<fx>.cliente.json --allowed ../mudancas/<fx>` → `runlog evaluation` (`canary`).
2. Avaliador: subagente novo com [AVALIADOR.md](AVALIADOR.md). Guardar a tabela em `../execucoes/<run>/avaliacao.json`.
3. `f8 verify-eval --engagement ../execucoes/<run>/snapshots/<último>/engagement --eval … --fixture <fx> [--expected-extra …]`; `runlog evaluation` com `counts` e o veredicto do verify.
4. A tabela vai ao mantenedor (Q4).

## 6. Regras do orquestrador

- Literal: o que passa de um papel para outro passa sem edição; qualquer nota do orquestrador vai só para o run-log, marcada `note`.
- Nunca se continua um executor descartado; nunca se repõe um snapshot por cima de um engagement.
- Uma falha do runtime é registada tal como veio e fica: a execução segue se o runtime deixar seguir; uma causa sistémica corrige-se no F8.4 e os cenários afectados repetem-se, guardando o resultado falhado.
- Mudança de sessão: antes de sair, run-log, snapshot e relatório da fase com push.
