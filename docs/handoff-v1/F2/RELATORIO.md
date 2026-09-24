# F2 — Relatório da fase (continuidade transacional mínima)

Estado: **completed** (2026-09-23). Gate T09–T17 cumprido e aceite pelo mantenedor, com o limite declarado da T10. Desenho e decisões Q1–Q6: [DESENHO.md](DESENHO.md). Avaliação do gate: §5. F3 autorizado.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F2.1 Coordenador (read-set, códigos estáveis, envelope) + bootstrap `inputs` + D17 | integrado | `7f10fb5` | `test_handoff_continuity.py` 15 casos (T11, T12 em 5 limites, T13, T14 com 4 corridas de 2 processos, D17). Full 82/82 ficheiros, 2732 testes; stdlib 63/63, 1934; ambos exit 0 |
| F2.2 Rascunho/publish/reconcile, on-su-mirror a só reportar | integrado | `ee0a8a1` | `test_handoff_publish.py` 17 casos (T17, T13, T11 sobre rascunho, integridade, CLI e envelope); `test_lens_mirror` L1 adaptado; W8d do `/start` passa pelo passo 9c. Full 83/83, 2749; stdlib 64/64, 1951; ambos exit 0 |
| F2.3 Checkpoint, tarefas, `INCOMPLETE_READ_SET` | integrado | `630194b` | `workflow.py task plan|start|receive|reconcile|show`. Checkpoint publicado pelo coordenador; `publish` de um rascunho com tarefa integra-a na mesma operação. `/round` regista cada lente como tarefa (4a1). `test_handoff_checkpoint.py` 22 casos (T10, T15, T12, T13, reconciliação, integridade, CLI). Full 85/85, 2784; stdlib 66/66, 1986; ambos exit 0 |
| F2.4 Retoma a frio | integrado | `a7af14c` | `workflow.py resume` só lê: perfil → bootstrap com o checkpoint no read-set → checkpoint → reconciliação proposta → frescura recalculada → contexto com orçamento (ids de todos os críticos sempre) → próxima acção com razão. `/status` 2b e `/resume` consultam-no. `test_handoff_resume.py` 9 casos (T09 num processo novo, T16, D02, recuperação, legado, objectivo por declarar). Full 86/86, 2793; stdlib 67/67, 1995; ambos exit 0 |
| F2.5 Skills das 6 autoridades + nascimento | integrado | `e3c0c0f` | protocolo único em `orchestration.md` → *Writing an authority*; 15 escritores convertidos (6+1 lentes, `/round`, chairman, `/frame`, `/options`, `/decide`, `/answer`, `/blueprint`, `/start`); `/capture` deixou de escrever `_state.json`. Nascimento = `init` + 1 publicação (W8d). `test_handoff_skill_writes.py` 12 casos. Full 84/84, 2762; stdlib 65/65, 1964; ambos exit 0 |
| F2.6 Coverage (D07), su-confirmed-guard, H2 | integrado | `ccb1379` | `finalize` pelo coordenador: idempotente, versão = maior emitida + 1 contando os recibos, `.json`+`.md` numa operação com `expected=""` e as fontes como read-set; `su-confirmed-guard` retirado; slugs reais fora dos ficheiros normativos e do motor; `_drafts/`/`_work/` fora do inventário. D09 e `capture_run` já tinham fechado em F2.5. Full 86/86, 2797; stdlib 67/67, 1999; ambos exit 0 |
| F2.7 Gate | integrado | (este) | teste de contrato da janela da projecção (`D17_ProjeccaoNumaRevisao.test_every_file_the_model_reads_is_inside_the_window`); `handoff-contract.md` → *Checkpoint* diz como ficou; §5–§8 abaixo |

## 2. Defeitos do F0 fechados

| ID | Como | Teste |
| --- | --- | --- |
| D08 | `operation.run(read_set=…)`: input só de leitura verificado sob o lock, antes do staging → `STALE_INPUT` | T11_ReadSet |
| D19 | A promoção de estado no sítio já não é espelhada em silêncio: o hook só reporta, `reconcile` nomeia as mudanças de estado material antes de publicar, e o guarda e o `publish` recusam `Confirmed` sem prova (regra única `workflow.su_problems`) | L1 `test_a_state_promotion_in_place_is_named_before_it_is_mirrored`; `Integridade` |
| D09 | Linha `D-NNN` do `/decide` com as 7 células de `## Confirmed`, e uma classe de localizador própria para linhas `D-` (decisão Q5) | `LinhaDeDecisao` |
| D07 | `coverage finalize` publica pelo coordenador; o mesmo rascunho devolve a mesma versão, e um número apagado nunca se reutiliza | `Finalize.test_the_same_draft_twice_is_the_same_version`, `test_a_deleted_version_number_is_never_reused`, `test_the_publication_is_one_coordinator_operation` |
| D17 | `projection.operational_state`: o modelo é lido com os seus ficheiros declarados como inputs do bootstrap, e o marcador de estado é revalidado depois do modelo. Se mudou, repete; se continuar a mudar, `CONCURRENT_WRITE` | D17_ProjeccaoNumaRevisao |

## 3. Testes adaptados

- `test_audit_findings.F02`: o substituto de `snapshot` aceita o novo argumento `inputs` (mudança de assinatura; a garantia testada não muda).
- `test_lens_mirror.L1` (disposição F0 «adaptar»): o hook já não espelha. Os três casos passam a provar a T17: edição preservada, reportada, escrita seguinte recusada, reconciliação explícita. Mais a promoção no sítio nomeada e seis escritas de lente seguidas pelo coordenador sem bloqueio. L2/L3 intactos.
- `test_graph_birth.W8d`: o nascimento é `init` + um rascunho com todo o scaffold + uma publicação. Novo caso: um `M-n` cujo alvo não está no rascunho é recusado.
- `test_coverage_integration` (disposição «manter», caminho de publicação decidido em Q3): a fixture sintética `fx-coverage-f06` ganhou o bloco `workflow` (o coordenador recusa a versão histórica), e o digest novo do seu `_state.json` foi posto nos 19 registos que o citavam. Os casos que republicavam o mesmo rascunho passam a provar a idempotência. Os de versão seguinte e de concorrência usam rascunhos com conteúdo distinto. «Escreve só em `_coverage/`» passa a admitir o recibo em `_ops/`. Novos: número apagado não se reutiliza, uma operação com recibo, legado recusado.
- `test_pp_architecture_templates` e `test_handoff_legacy.D02`: o título fixado mudou (`Flip state to Decision (through the coordinator)`; `9. Write, in the birth-draft copies, …`); a garantia testada não muda.

## 4. Limitações conhecidas

- ~~Entre F2.2 e F2.5, as skills que editavam a SU no sítio deixavam o engagement por reconciliar.~~ Fechada em F2.5.
- O contrato das skills é textual (`test_handoff_skill_writes.py`). Prova que as instruções mandam usar rascunho e publicação, e que os comandos existem no motor. Não prova que uma sessão real as segue. O motor recusa o desvio: uma edição no sítio bloqueia até reconciliar (T17), e um `mv` por Bash sobre `_state.json` fica fora dos hooks. Essa última limitação continua declarada.
- `INCOMPLETE_READ_SET` vê citações, não leituras. O mapa id→ficheiro de `resolve.CITED_IDS` cobre `D-`, `TW-`, `O-NNN`, `M-n`, `PM-`/`PM-U-` e as linhas da SU, mais caminhos do engagement e nomes de ficheiros de `inputs/` e `_capture/`. Um input lido que não deixou citação fica fora da garantia. Só as linhas acrescentadas são verificadas.
- O schema `handoff-work/1` ganhou `results[].sha256`, um campo opcional e aditivo. A versão não mudou; um leitor antigo reporta-o como desconhecido e preserva-o.
- H2 ficou feito nos ficheiros normativos (skills, hooks, kernel, pack, comandos) e no motor (`dashboard.py`, `CALIBRACAO` anonimizado). Dois testes de integração em `library/kernel/tools/tests/` (`test_fields_draft`, `test_text_extract`) continuam a nomear pilotos reais: só correm com o engagement montado e saltam sem ele. A disposição do F0 manda-os consolidar em F4.
- O nascimento são duas operações: o `init` do grafo e a publicação do scaffold. Entre as duas, o engagement só tem o grafo, sem `_state.json`. Um `/start` repetido pára, porque a pasta já existe. A recuperação é abrir o rascunho e publicar, sem apagar nada.
- ~~As linhas `[ÂMBITO AUTORIZADO]` de `states.md` regra 3 não tinham classe de localizador.~~ Decidido em Q6 (2026-09-23): com a marca, um `C-` pode citar `decisions.md#D-NNN` de uma aprovação (frame, solução, desenho) presente; sem a marca, continua recusado (`LinhaDeDecisao.test_an_authorized_scope_row_cites_an_approval`).
- O guarda passou a recusar também a remoção de uma linha da SU (`SU_ROW_REMOVED`). A regra (append-only) já era do kernel; faltava quem a impusesse.

- ~~`MODEL_INPUTS` enumera o que `build_model` lê hoje; uma leitura nova fora da lista ficava fora da janela.~~ Mitigada em F2.7: o teste de contrato espia as leituras do modelo na fixture mais rica e falha se alguma, de um ficheiro existente, cair fora das autoridades, dos inputs declarados (semântica real de `Path.glob`) ou de `_ops/`.

## 5. Gate (05_FASES F2: T09–T17)

| Teste | Critério (06_VALIDACAO) | Estado | Evidência |
| --- | --- | --- | --- |
| T09 | Cold resume sem conversa anterior reconstrói objectivo, autorizações, bloqueios e próximo trabalho | **cumprido** | `test_handoff_resume.T09_RetomaAFrio`: processo novo (CLI) sobre um engagement deixado a meio por uma sessão morta; a próxima acção acompanha o estado depois de cada passo |
| T10 | Read-set omite input usado → `INCOMPLETE_READ_SET`; não publicável | **cumprido, com limite** | `test_handoff_checkpoint.T10_ReadSetIncompleto` (receive e publish recusam). Limite: vê citações, não leituras (§4) |
| T11 | Input muda durante a execução → `STALE_INPUT`; rascunho preservado; integração rejeitada | **cumprido** | `test_handoff_continuity.T11_ReadSet` (coordenador); `test_handoff_publish.T11_RascunhoDesactualizado`; `test_handoff_checkpoint.T11_InputDaTarefaMudou` |
| T12 | Falha em cada limite de publicação → revisão velha/nova ou `RECOVERY_REQUIRED`, nunca mistura válida | **cumprido** | `test_handoff_continuity.T12` (5 limites de uma operação de 3 ficheiros; bootstrap e projecção nunca dão pronto; recuperação completa e idempotente); `test_handoff_checkpoint.T12` (falha com checkpoint); `test_operation_recovery` mantido |
| T13 | Repetir após sucesso sem resposta → mesmo efeito/recibo, sem duplicar | **cumprido** | `T13` em continuity (coordenador), publish (rascunho), checkpoint (dupla integração) e coverage (`test_the_same_draft_twice_is_the_same_version`) |
| T14 | Duas sessões da mesma base → conflito explícito; nada se perde | **cumprido** | `test_handoff_continuity.T14` (2 processos reais, 4 corridas: uma publica, a outra recebe `STALE_INPUT`/`CONCURRENT_WRITE`, o ficheiro tem o que o recibo diz); `test_handoff_publish` (rascunho de outra sessão → `STALE_INPUT`, a publicação alheia fica) |
| T15 | Resultado recebido e não integrado não conta para readiness; aparece na retoma | **cumprido** | `test_handoff_checkpoint.T15_RecebidoNaoIntegrado`; `test_handoff_resume` (`results_pending`, frescura recalculada) |
| T16 | Contexto excede orçamento → estado parcial explícito e expansão; nenhum crítico omitido | **cumprido** | `test_handoff_resume.T16_OrcamentoExcedido` |
| T17 | Edit directo na SU, grafo divergente → preservar, bloquear publicação inconsistente, reconciliar explicitamente | **cumprido** | `test_handoff_publish.T17_EdicaoDirecta`; `test_lens_mirror.L1` |

**«Nenhum leitor considera conjunto misto como revisão válida»:** o bootstrap valida a revisão com os inputs declarados (F2.1). A projecção lê o modelo dentro da janela (D17, com o teste de contrato da janela). A retoma põe o checkpoint no read-set. Os leitores de T12 nunca dão pronto sobre uma publicação a meio. **Cumprido.**
**«Dupla integração é idempotente»:** T13 nas quatro vias de escrita (coordenador, rascunho, tarefa, coverage). **Cumprido.**

Trabalho do plano (05_FASES F2, itens 1–7):

1. checkpoint por referências (F2.3);
2. read-set com hashes e revisão consumida (F2.1);
3. checkpoint e autoridades no coordenador, com recibos e conflitos verificáveis (F2.2, F2.3, F2.5);
4. drafts nunca consumidos; stale e repetição tratados (F2.2, F2.3);
5. diagnóstico, recuperação e cold resume com orçamento (F2.4);
6. hooks só como guarda e detecção, edição directa e reconciliação documentadas (F2.2; HOOKS.md; `orchestration.md` → *Writing an authority*);
7. falha injectada e duas sessões (F2.1, F2.3).

Todos feitos.

Rollback (plano): as revisões novas ficam preservadas (recibos em `_ops/`). Desligar a escrita experimental é voltar a `ba0c27b`/`85baf10` para engagements legados (decisão A). Um engagement handoff-v1 recupera com `operation.py recover`.

## 6. Leitor, escritor e schema — o que F2 acrescenta

Complementa `../F1/LEITOR-ESCRITOR.md`.

| Dado | Schema | Escritor | Leitores | Guarda |
| --- | --- | --- | --- | --- |
| `_drafts/<id>/` + `_draft.json` | `aisa-draft/1` | `resolve.draft` (cópias); a skill edita as cópias | `resolve.publish`, `workflow.task_receive` | Não é autoridade: fora de todo o read-set, do inventário do coverage e do dashboard |
| `_work/checkpoint.json` | `handoff-work/1` (+ `results[].sha256` opcional) | `workflow.task_*` e `resolve.publish` (tarefa), sempre por `operation.run` | `workflow.resume`, `/status` 2b, `/resume`, projecção (input) | Escrita por ferramenta recusada (`_work/` coordenado); ilegível ou schema futuro nunca se sobrescreve |
| Recibo `_ops/receipts/<op>.json` | + `read_set` | `operation.run` | quem repete a operação; `coverage.issued_versions` | Escrita por ferramenta recusada |
| `_coverage/coverage_vNN.{json,md}` | coverage schema 1 | `coverage.finalize` por `operation.run` | coverage, `/blueprint`, `/render`, `/status` | `expected=""`; versão = maior emitida + 1 |
| Autoridades (6) | — | `resolve.publish` (rascunho) e os motores `resolve`/`migrate`; nunca edição no sítio | todos | guarda: integridade (`workflow.su_problems`/`state_problems`) antes da escrita; edição directa preservada e bloqueada até `reconcile` |

## 7. Decisões e pontos por decidir

- Q1–Q5: DESENHO.md, todas decididas pelo mantenedor em 2026-09-23.
- Q6 (2026-09-23): `[ÂMBITO AUTORIZADO]` estende a regra do registo de decisão — cita uma aprovação presente, e só com a marca.
- Fecho: gate aceite pelo mantenedor em 2026-09-23, com o limite da T10 como limitação conhecida.

## 8. Próxima fase

F3 (05_FASES): análise integrada e materialidade funcional. Recebe a metade de cobertura por lente do T07, aceite como excepção em F1. Pontos que ficam para fases posteriores, cada um com dono:

- D06 (`render-validate` não idempotente) → F6;
- D10 (`migrate restore --force`) → F7;
- testes de integração com pilotos reais → F4;
- a limitação das escritas por Bash (§4) → sem fase; o motor recusa o desvio.
