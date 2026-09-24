# F7 — Relatório da fase (mudanças, migração e compatibilidade)

Estado: **gate avaliado — aguarda aceitação** (2026-09-24). Desenho e decisões Q1–Q4: [DESENHO.md](DESENHO.md). Gate: T35/T36/T41/T42; o rollback preserva a informação nova e bloqueia o downgrade destrutivo.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F7.1 Raio de impacto | integrado | (este) | `library/kernel/tools/impact.py` (só leitura): `edges` (dependências que os artefactos já registam: linha → FC/âmbito/WP/candidato/nó do desenho, FC → WP, candidato → parecer da revisão corrente, unidade de conhecimento → parecer), `stale` (derivado em cada leitura, Q1: `ROW_RESOLVED`, `ROW_WITHDRAWN`, `ROW_MISSING`, `ROW_CHANGED`, `VIA_CONTRACT`, `VIA_CANDIDATE`, `KNOWLEDGE_CHANGED`, com a cadeia; `bytes` = revisão de bytes exacta, informativa; `unverified` = linha citada sem impressão registada), `impact --changed` (raio antes de publicar + citações por texto do `resolve.cited_by`, candidatos). **Impressão por linha** (decisão do mantenedor, 2026-09-24): `functional.py`, `inventory.py`, `review.py` juntam a `based_on`, ao publicar, `shared-understanding.md#<id>` com `row` (`state`, `criticidade`, `resolved`, `retired`) e o seu `sha256`, calculada da SU que o read-set do rascunho fixa. `handoff-contract.md` → *Dependencies*. Matriz F0: 2 entradas. `test_impact.py` 14 casos. Full 109/109, 3018; stdlib 90/90, 2220; ambos exit 0 |
| F7.2 Consumidores | integrado | (este) | `impact.blocking` (FC, âmbito e WP fora das exclusões autorizadas). `STALE_PREMISE` bloqueia a versão final em `functional.render_gate` (só os FC que o deliverable cita), `trace.scope_gate` e, por ele, `release.readiness` (motivo explícito; pacote `preliminary`). Candidatos, pareceres, nós do desenho e itens excluídos informam. `projection.py`: `stale_dependents` com `blocks_final` e uma linha no `explain`; não fecha a transição de fase. Skills: `/answer` passo 7 começa por `impact.py impact` e `stale`; `/status` 1b lê `stale_dependents`; `/render` 7b nomeia `STALE_PREMISE`. `test_impact_gates.py` 5 casos (T41 ponta a ponta: premissa respondida → render, âmbito e release recusam com a cadeia `A-001 → FC-0001 → WP-0001`; o FC não afectado sai; republicar com a sucessora pede nova autorização; autorizado, pronto de novo; dependente de item excluído informa). Full 110/110, 3023; stdlib 91/91, 2225; ambos exit 0 |
| F7.3 Versões suportadas, D10, rollback | integrado | (este) | `workflow.SUPPORTED` (tabela única, 10 artefactos), `supported_schema`, `schema_problem`, `SchemaError`. Leitores novos na verificação: `review._load` (candidatos, pareceres, mandatos, registo), `impact._load`, `trace._load`, `release.verify` (índice). Já verificavam: estado, checkpoint, FC, âmbito, inventário. **D10**: `migrate.restore` sem `force` (parâmetro e `--force` do CLI retirados); com trabalho posterior recusa sempre. Rollback: o código de `56cb4e1` (fim da F5), extraído por `git archive`, publica em `decisions.md` num engagement da F6 com release; âmbito, inventário e `_release/` ficam byte a byte; o código de agora volta a construir e verificar o release. `handoff-contract.md` → *Supported versions and rollback*. `test_f7_compat.py` 10 casos (tabela = constantes dos motores; T36 alargado: 7 artefactos × leitores, recusa sem tocar; sem `schema_version`; publicação recusada antes de escrever; índice de outra versão; D10 ×2; rollback ×2). T35 não aplicável por decisão (opção A). Full 111/111, 3033; stdlib 92/92, 2235; ambos exit 0 |
| F7.4 Docs | integrado | (este) | Q5 decidida (doc novo + actualizar). `docs/OPERACAO.md` novo: setup (suites, CI com `fetch-depth: 0`), manutenção (`library/` por commit, matriz F0, `stdlib-tests.txt`, versão nova de artefacto = `workflow.SUPPORTED` + schema no mesmo commit), recuperação (tabela sintoma → diagnóstico → acção com `operation`, `bootstrap`, `graph verify`, `resolve reconcile`, `impact stale`, `release verify`, `migrate restore`; o que nunca se faz; rollback de código), acesso e backup (tabela por artefacto; o que o código não define fica dito). Cada comando conferido contra o `--help` do motor. `ARCHITECTURE.md` v3.6.0: entrada de changelog do handoff-v1 F1–F7; notas em §3.4 e §7.3 (council e personas retirados, o texto anterior fica como registo); §6 com skills, comandos, agentes, memória por papel, hooks, contratos, schemas e os 7 motores novos; `/frame`, `/options`, `/retro` na tabela de comandos; nota em §10.2. `ONBOARDING.md`: diagrama, passos `/frame` e `/options`, referência rápida (agentes, memória, `_design/`, `_release/`, contrato, operação), ponteiro de recuperação. Ligações em `README.md` e `CLAUDE.md`. Matriz F0: `OPERACAO.md` como menção (SU, estado). Full 111/111, 3033; stdlib 92/92, 2235 |
| F7.5 Relatório e gate | integrado | (este) | §6–§8 |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F7.0 | levantamento e desenho | precisa do contexto da sessão; o detalhe volta a ser preciso | na sessão |
| F7.1 | motor, publicação, testes | idem | na sessão |
| F7.2 | consumidores, skills, testes | idem | na sessão |
| F7.3 | versões, D10, rollback, testes | idem | na sessão |
| F7.4 | docs | idem: o conteúdo é o estado do código das fases | na sessão |

## 3. Testes adaptados

- Nenhum em F7.1: a impressão por linha acrescenta entradas a `based_on`, que nenhum teste existente fixa.
- Nenhum em F7.3: nenhum teste passava `force=True` a `migrate.restore`.
- Nenhum em F7.2: nenhuma fixture existente tinha dependente sobre premissa mudada fora das exclusões (verificado: suites verdes sem alteração).

## 4. Limitações conhecidas

- O estado de uma linha é a secção onde está: uma linha com o mesmo id movida para outra secção deixa de ser lida como linha, e os dependentes vêem-na como inexistente (`ROW_MISSING`), não como `ROW_CHANGED`. O resultado para o gate é o mesmo; a mensagem é menos precisa.
- Artefactos publicados antes do F7.1 (incluindo o pacote congelado da F6) não levam impressão por linha: vêem resolvida, retirada e inexistente; estado/criticidade mudados no sítio aparecem como `unverified` até à próxima publicação.
- Os nós do desenho não têm impressão (o desenho é escrito pelo autor, a aprovação fixa o `sha256` do ficheiro): só resolvida, retirada e inexistente.
- `KNOWLEDGE_CHANGED` compara o `sha256` gravado no mandato com o ficheiro actual do repositório; a prova simula a mudança editando o mandato (nenhum teste escreve em `library/`).
- Uma linha `Confirmed` não se retira (P-21 é só para perguntas; `dashboard.parse_su` ignora o marcador): mudar uma premissa confirmada faz-se por transição nova, e a antiga só fica desactualizada para os dependentes quando o conteúdo passa a outra linha (resolvida/movida).

## 5. Retoma (para uma sessão nova)

Estado depois do F7.5: F7 completa, gate avaliado, **aguarda aceitação do mantenedor**. Full 111/111 e stdlib 92/92 verdes.

Próxima acção segura: pedir ao mantenedor, por `AskUserQuestion`, a aceitação do gate da F7 com os limites de §4 e §6. Aceite → marcar *concluída — gate aceite* aqui e no `README.md`, e só com autorização explícita abrir a F8 (desenho primeiro, §0 subagentes, decisões ao mantenedor antes de código).

Regras que continuam: decisões de contrato vão ao mantenedor antes de código; subagentes só pela regra do README; suites completas antes de cada push; avisar quando mudar de sessão.

## 6. Gate (05_FASES F7: T35/T36/T41/T42; rollback preserva novas informações e bloqueia downgrade destrutivo)

| Teste | Critério (06_VALIDACAO) | Estado | Evidência |
| --- | --- | --- | --- |
| T35 | Migração de engagement antigo, se necessária em F0 → dados/estados/decisões preservados; campos novos sem evidência por completar | **não aplicável por decisão** | F0 opção A (sem classic, sem migração); F7 Q4 (sem suporte sem consumidor). A recusa segura de um engagement antigo é o T03 da F1 (`test_handoff_legacy` T03_*) |
| T36 | Leitor antigo encontra schema novo → falha clara/read-only; sem truncar campos | **cumprido** | F1: código histórico real `ba0c27b` recusa escrever num engagement novo (`test_handoff_legacy.T36_LeitorAntigo`); estado de versão futura → `SCHEMA_UNSUPPORTED` sem tocar no ficheiro (`test_handoff_workflow.T36_SchemaFuturo`). F7: `workflow.SUPPORTED` + todos os leitores dos artefactos handoff recusam outra versão sem tocar em nenhum ficheiro, publicação recusada antes de escrever, índice de release de outra versão não verifica (`test_f7_compat.Tabela`, `T36Alargado`) |
| T41 | Premissa altera regra/dados/arquitectura → dependências reais stale; itens não afectados preservados | **cumprido** | `test_impact.T41` (resposta, retirada, criticidade no sítio, premissa de candidato → parecer, nó do desenho, artefacto sem impressão; raio antes de publicar com os não afectados); `test_impact_gates.T41PontaAPonta` (render final, gate de âmbito e release recusam com a cadeia `A-001 → FC-0001 → WP-0001`; o FC não afectado sai; republicar com a sucessora pede nova autorização; dependente de item excluído informa) |
| T42 | Mudança só editorial ou unidade não consumida do pack → sem reabertura semântica; byte revision exacta | **cumprido** | `test_impact.T42` (espaços na linha, `verificado_em` renovado, byte do desenho mudado → revisão de bytes exacta sem achado; só a unidade do pack que o mandato consumiu chega ao parecer); `test_impact.Impressao` (republicar sem mudança de conteúdo mantém a impressão do FC) |
| Rollback preserva informação nova | — | **cumprido** | `test_f7_compat.RollbackDeCodigo`: o código de `56cb4e1` publica num engagement da F6 sem tocar em âmbito, inventário nem `_release/`; o código de agora volta a construir e verificar o release |
| Bloqueia downgrade destrutivo | — | **cumprido** | D10: `migrate.restore` sem `force`; com trabalho posterior recusa sempre e a decisão nova fica (`test_f7_compat.D10`, `test_migration.M06_TrabalhoPosterior`) |

## 7. Itens do plano (05_FASES F7)

| Item | Estado |
| --- | --- |
| 1. Raio de impacto e stale transitivo reutilizando grafo/fingerprints | feito: `impact.py` reutiliza as referências já registadas, o `resolve.cited_by` e o modelo de `graph.GATE_FIELDS`; impressão por linha em `based_on` |
| 2. Migração dry-run, backup validado, versão suportada, relatório de campos não mapeados | versão suportada feita (`workflow.SUPPORTED`). Dry-run e backup já existiam em `migrate.py` (legado → grafo) e não mudam; migração nova e relatório de campos não mapeados não construídos (Q4: sem consumidor) |
| 3. Novo handoff e rejeição segura de versões não suportadas; engagement antigo, migração interrompida, leitores anteriores só nos caminhos de F0 | feito: T36 alargado; engagement antigo recusado (T03, F1); migração interrompida recuperável (`test_migration.M06_TrabalhoPosterior.test_a_pending_operation_is_recoverable_after_a_half_migration`); leitor anterior = código do fim da F5 e versão histórica |
| 4. Não promover factos, inventar aprovações nem transformar pareceres antigos em revisão independente | cumprido: `impact.py` não escreve; sair do `stale` exige republicar pelo autor, e um FC com conteúdo mudado volta a pedir autorização humana (`test_impact_gates`); nenhuma migração que converta pareceres |
| 5. Docs de setup, manutenção, recuperação e responsabilidades de acesso/backup | feito: `docs/OPERACAO.md`; `ARCHITECTURE.md` v3.6.0 e `ONBOARDING.md` actualizados (fecha o desvio registado na F5 e na F6) |

## 8. Próxima fase

F8 — pilotos adversariais e aceitação do destinatário (`../plan/05_FASES.md`): protocolo de `06_VALIDACAO.md` nos três percursos, qualidade face aos requisitos, retoma a frio com mudança de premissa a meio, destinatário com só o pacote, slice numa sandbox só com autorização e recursos. Gate T43–T46: exige julgamento humano ou avaliação assistida documentada; uma simulação não reivindica aceitação humana. Não começa sem autorização explícita do mantenedor.
