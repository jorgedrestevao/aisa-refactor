# F2 — Relatório da fase (continuidade transacional mínima)

Estado: **in_progress** (autorizada em 2026-09-23). Desenho e decisões Q1–Q4: [DESENHO.md](DESENHO.md).

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F2.1 Coordenador (read-set, códigos estáveis, envelope) + bootstrap `inputs` + D17 | integrado | `7f10fb5` | `test_handoff_continuity.py` 15 casos (T11, T12 em 5 limites, T13, T14 com 4 corridas de 2 processos, D17). Full 82/82 ficheiros, 2732 testes; stdlib 63/63, 1934; ambos exit 0 |
| F2.2 Rascunho/publish/reconcile, on-su-mirror a só reportar | integrado | (este) | `test_handoff_publish.py` 17 casos (T17, T13, T11 sobre rascunho, integridade, CLI e envelope); `test_lens_mirror` L1 adaptado; W8d do `/start` passa pelo passo 9c. Full 83/83, 2749; stdlib 64/64, 1951; ambos exit 0 |
| F2.3 Checkpoint, tarefas, `INCOMPLETE_READ_SET` | por fazer | | |
| F2.4 Retoma a frio | por fazer | | |
| F2.5 Skills das 6 autoridades + nascimento | por fazer | | |
| F2.6 Coverage (D07), su-confirmed-guard, H2, D09, capture_run | por fazer | | |
| F2.7 Gate | por fazer | | |

## 2. Defeitos do F0 fechados

| ID | Como | Teste |
| --- | --- | --- |
| D08 | `operation.run(read_set=…)`: input só de leitura verificado sob o lock, antes do staging → `STALE_INPUT` | T11_ReadSet |
| D19 | A promoção de estado no sítio já não é espelhada em silêncio: o hook só reporta, `reconcile` nomeia as mudanças de estado material antes de publicar, e o guarda e o `publish` recusam `Confirmed` sem prova (regra única `workflow.su_problems`) | L1 `test_a_state_promotion_in_place_is_named_before_it_is_mirrored`; `Integridade` |
| D17 | `projection.operational_state`: o modelo é lido com os seus ficheiros declarados como inputs do bootstrap, e o marcador de estado é revalidado depois do modelo. Se mudou, repete; se continuar a mudar, `CONCURRENT_WRITE` | D17_ProjeccaoNumaRevisao |

## 3. Testes adaptados

- `test_audit_findings.F02`: o substituto de `snapshot` aceita o novo argumento `inputs` (mudança de assinatura; a garantia testada não muda).
- `test_lens_mirror.L1` (disposição F0 «adaptar»): o hook já não espelha. Os três casos passam a provar a T17: edição preservada, reportada, escrita seguinte recusada, reconciliação explícita. Mais a promoção no sítio nomeada e seis escritas de lente seguidas pelo coordenador sem bloqueio. L2/L3 intactos.
- `test_graph_birth.W8d`: as linhas `R-00` do `/start` entram pelo passo 9c (rascunho → publish), porque o hook já não as espelha.

## 4. Limitações conhecidas

- **Entre F2.2 e F2.5**, as skills que ainda editam a SU no sítio (lentes, `/round`, chairman, `/answer`, `/decide`, `/frame`, `/options`, `/capture`) deixam o engagement por reconciliar depois de cada escrita. O guarda recusa a escrita seguinte até `resolve.py reconcile --apply`. O `/start` já está convertido (passo 9c). F2.5 converte as restantes; é o próximo incremento.
- O guarda passou a recusar também a remoção de uma linha da SU (`SU_ROW_REMOVED`). A regra (append-only) já era do kernel; faltava quem a impusesse.

- `MODEL_INPUTS` enumera o que `build_model` lê hoje. Uma leitura nova no dashboard que não se declare aqui fica fora da janela. Mitigação em F2.7: um teste de contrato que compare as leituras do modelo com a lista.
