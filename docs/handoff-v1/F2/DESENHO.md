# F2 — Desenho da continuidade transacional mínima

Plano: `../plan/05_FASES.md` F2 e `../plan/04_CONTINUIDADE.md`. Gate: T09–T17 (`../plan/06_VALIDACAO.md`).

Decisões do mantenedor (2026-09-23), todas na opção recomendada:

| # | Decisão | Escolha |
| --- | --- | --- |
| Q1 | Como as skills escrevem a SU em `handoff-v1` | Pelo coordenador: rascunho em `_drafts/` e `resolve.py publish`. Um Edit directo é preservado e detectado, e bloqueia até `resolve.py reconcile` explícito. O hook deixa de publicar sozinho |
| Q2 | Âmbito de F2 | Os escritores das 6 autoridades (`_state.json`, SU, `answers.md`, `decisions.md`, `context.json`, `enquadramento.md`). Os artefactos de fase ficam para F4–F6 |
| Q3 | `coverage finalize` (D07) | Pelo coordenador: um só mecanismo de publicação. A idempotência vem do conteúdo do rascunho; a versão é a maior emitida + 1, nunca reutilizada |
| Q4 | `su-confirmed-guard` | Retirado. A regra fica em `dashboard.audit_confirmed_locators`, consultada pelo guarda e pelo coordenador |
| Q5 | Linha `D-NNN` na SU (o `/decide` era recusado desde F1: `decisions.md#D-NNN` não é localizador das cinco classes) | Classe própria só para ids `D-`: localizador `decisions.md#D-NNN`, com o bloco presente (conta se for publicado na mesma operação). Um facto nunca se confirma citando `decisions.md` (`states.md` → *Confirmed threshold*) |

Nenhum motor novo. `operation.py` continua a ser o único publicador e `bootstrap.py` a única reconstrução. `resolve.py` continua dono do espelho SU→grafo. O `workflow.py` só liga tarefa, inputs e próxima acção a estes três.

## 1. Coordenador: read-set e códigos estáveis

`operation.run(eng, op_id, write_set, expected=None, read_set=None)`:

- `read_set = {rel: sha256}` são inputs consumidos que **não** se escrevem. São verificados sob o lock, depois da pendência e antes do staging. Um digest diferente dá `STALE_INPUT`: nada é preparado, nada é publicado, e o rascunho de quem chamou fica intacto (D08, T11). Um caminho que esteja no `write_set` e no `read_set` ao mesmo tempo é recusado como pedido mal formado: a base de um ficheiro escrito declara-se em `expected`.
- A intenção e o recibo registam o `read_set`. `request_hash` inclui-o quando existe. Sem `read_set`, o hash é o de sempre, e os recibos antigos continuam a reconhecer-se.
- `stable_code(code)` mapeia os códigos de origem para os códigos estáveis do contrato (02 §Respostas):
  - `BASE_CHANGED`, `STALE_INPUT` → `STALE_INPUT`;
  - `PENDING_EXISTS`, `PENDING_UNREADABLE`, `THIRD_STATE`, `STAGING_INCOMPLETE`, `STAGING_CORRUPT`, `INTENT_VERSION` → `RECOVERY_REQUIRED`;
  - `VERIFY_FAILED`, `RECEIPT_MISMATCH` → `INTEGRITY_FAILURE`;
  - `LOCK_ACTIVE`, `LOCK_UNDETERMINED`, `LOCK_CONTENDED`, `LOCK_UNREADABLE` → `CONCURRENT_WRITE`, um código a mais que o mínimo do contrato permite.

  O código de origem continua no detalhe (`source_code`). `response_from_error` devolve o envelope `handoff-response/1`.

## 2. Bootstrap: read-set declarado e revisão consumida

`bootstrap(eng, budget, inputs=())`. `inputs` são caminhos ou globs relativos ao engagement, declarados pela tarefa (blueprint, frame, options, `_capture/…`, pack). Entram no snapshot com o digest dos bytes. `snapshot.input_revision` cobre as autoridades e os inputs, e a janela de `consistent_read` passa a cobri-los: uma escrita num input durante a leitura repete a leitura. Um input declarado que não existe fica registado com digest `""`, porque ausência é um estado. O digest nunca inclui recibos nem logs (`_ops/`, `_migration/`, `_drafts/`), para o read-set não se digerir a si próprio.

**D17.** Hoje `projection.operational_state` lê `build_model` fora da janela. Passa a declarar como inputs os ficheiros que o modelo lê e, depois de os ler, a validar o marcador de estado contra o do bootstrap. Se mudou, repete. Se continuar a mudar, bloqueia com `CONCURRENT_WRITE` e nunca apresenta o estado misto.

## 3. Rascunho e publicação (Q1, Q2)

```
resolve.py draft   --engagement E --files <rel>... [--reads <rel|glob>...] [--task TASK-NNN]
  → _drafts/<DRAFT-id>/<rel> (cópias) + _drafts/<DRAFT-id>/_draft.json
    {base: {rel: sha256}, reads: {rel: sha256}, task, created_at}
(a skill edita as cópias com Edit/Write — `_drafts/` não é autoridade)
resolve.py publish --engagement E --draft <DRAFT-id>
  → UMA operação: ficheiros mudados + espelho do grafo (se a SU mudou) + checkpoint (se há tarefa)
    expected = base do rascunho · read_set = reads do rascunho
```

Antes de publicar, com o conteúdo novo, correm as mesmas verificações que o guarda faz sobre um Edit:

- `Confirmed` sem localizador válido → `INTEGRITY_FAILURE` (regra única, `audit_confirmed_locators`);
- `_state.json` não perde chaves e não muda o bloco `workflow`;
- nenhuma linha da SU desaparece (append-only; as edições sancionadas mudam células, não apagam linhas).

Se a base mudou depois do rascunho, dá `STALE_INPUT`. O rascunho fica como está, para ser refeito sobre a base nova: nunca há last-writer-wins. Publicar o mesmo rascunho duas vezes dá o mesmo recibo, porque o `op_id` deriva do conteúdo e da base (T13). `publish` recusa um engagement cujo bootstrap não esteja pronto.

**Edição directa (T17).** Num engagement `handoff-v1`, o `on-su-mirror` deixa de publicar: escreve no stderr a divergência e o comando de reconciliação. O bootstrap passa a não pronto (`AUTHORITY_UNMIRRORED`/`AUTHORITY_DRIFT`), por isso o guarda recusa a escrita seguinte e o coordenador recusa publicar sobre o estado divergente. A edição fica nos ficheiros. `resolve.py reconcile --engagement E` mostra o que vai espelhar, com as mudanças de estado material destacadas; `--apply` publica pelo coordenador, com recibo. A SU prevalece, como sempre.

**Nascimento** (como ficou em F2.5). `/start` corre `migrate.py init` (grafo vazio, uma operação) e escreve depois o scaffold inteiro num rascunho: `context.json`, `_state.json`, SU com as linhas `R-00`, `council-log.md`, `decisions.md`, `answers.md`, `story.md` e `enquadramento.md`. Publica-o com `resolve.py publish` numa operação e num recibo, com o espelho das linhas `R-00`. A regra de `Confirmed` resolve os alvos no próprio rascunho (`overlay`), e por isso um `M-n` que cita `enquadramento.md#M-n` passa na mesma operação. Não existe `workflow.py birth`: um comando novo duplicaria o `publish`. O checkpoint inicial entra em F2.3. Fica fechada a sequência de escritas à mão (disposição F0 do `aisa-start`).

## 4. Checkpoint, tarefas e resultados

`_work/checkpoint.json` (`handoff-work/1`, congelado em F1). Leva só referências. Acrescentam-se dois campos opcionais, sem mudar a versão do schema:

- `results[].sha256`, o hash do manifesto do rascunho recebido;
- `results[].read_set`.

CLI `workflow.py task …`. Cada comando é uma operação do coordenador com `expected` sobre o checkpoint lido:

| Comando | Efeito |
| --- | --- |
| `plan --role R --criteria "…" [--input rel]… [--depends TASK-n]` | `TASK-NNN` `planned`. Um id nunca é reutilizado |
| `start TASK-n` | `running`; os `input_refs` ganham o sha256 dos bytes consumidos |
| `receive TASK-n --draft DRAFT-id` | resultado `received`, com a frescura calculada contra os inputs da tarefa. O rascunho fica em `_drafts/` e o checkpoint guarda o seu hash |
| `resolve.py publish --draft DRAFT-id` (tarefa no `_draft.json`) | resultado `integrated`, tarefa `completed`, `last_integrated_operation` e a mutação das autoridades, na mesma operação |
| `reconcile` | depois de uma falha: uma tarefa `running` com resultado recebido fica `blocked` (à espera de integração); sem resultado, volta a `planned`. Nunca se relança sozinha |

**`INCOMPLETE_READ_SET` (T10).** O rascunho só pode citar o que declarou ter lido. Cada id citado (`D-`, `TW-`, `M-`, `PM-`, linhas da SU) e cada caminho do engagement citado têm de estar cobertos pela base ou pelos reads do rascunho. Se não estiverem, `receive` e `publish` recusam, com os ids em falta. A verificação é determinística e não adivinha: o que ela não vê, citação implícita incluída, fica declarado como limitação.

**Resultado recebido e não integrado (T15).** Não entra na SU nem no grafo, por isso não conta para a prontidão nem para os gates. A retoma mostra-o, com a frescura.

## 5. Retoma a frio (T09, T16)

`workflow.py resume --engagement E [--budget N] [--json]` só lê. Segue a ordem de 04 §Retoma:

1. perfil;
2. bootstrap, com pendência → `RECOVERY_REQUIRED`;
3. checkpoint;
4. reconciliação proposta, sem a escrever;
5. frescura dos resultados;
6. contexto com orçamento: críticos primeiro, o omitido nomeado e a expansão sugerida (`--budget`), sem nunca deixar um bloqueio crítico fora sem o dizer;
7. próxima acção, com a razão pela qual é segura.

`/status` e `/resume` consultam-no.

## 6. Outras correcções de F2

- `coverage finalize` pelo coordenador (Q3, D07). A reserva `O_EXCL` sai, e a publicação dos dois ficheiros (`.json` e `.md`) passa a ser uma operação. As recusas `stale`/`changed-during` mantêm-se.
- `su-confirmed-guard` retirado (Q4).
- Slugs reais fora dos ficheiros normativos (H2).
- Template da linha `D` do `/decide` com 7 células (D09).
- `_state.json.capture_run` eliminado; a contagem deriva de `_capture/_capture-log.md`.
- `_drafts/` e `_work/` ficam fora do inventário do coverage e do separador Ficheiros.

## 7. Incrementos

| Inc. | Conteúdo | Testes |
| --- | --- | --- |
| F2.1 | Coordenador (read-set, códigos, envelope) + bootstrap `inputs` + D17 | T11, T12, T13, T14 |
| F2.2 | Rascunho/publish/reconcile + on-su-mirror a só reportar | T17, T13 |
| F2.3 | Checkpoint e tarefas + `INCOMPLETE_READ_SET` | T10, T15 |
| F2.4 | Retoma + `/status`/`/resume` | T09, T16 |
| F2.5 | Skills das 6 autoridades + nascimento pelo coordenador | cenário de nascimento, contratos das skills |
| F2.6 | Coverage (D07), su-confirmed-guard, H2, D09, capture_run | coverage integration adaptado |
| F2.7 | Relatório e gate | T09–T17 |
