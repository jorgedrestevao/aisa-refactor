# F2 — Relatório da fase (continuidade transacional mínima)

Estado: **in_progress** (autorizada em 2026-09-23). Desenho e decisões Q1–Q4: [DESENHO.md](DESENHO.md).

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F2.1 Coordenador (read-set, códigos estáveis, envelope) + bootstrap `inputs` + D17 | integrado | (este) | `test_handoff_continuity.py` 15 casos (T11, T12 em 5 limites, T13, T14 com 4 corridas de 2 processos, D17). Full 82/82 ficheiros, 2732 testes; stdlib 63/63, 1934; ambos exit 0 |
| F2.2 Rascunho/publish/reconcile, on-su-mirror a só reportar | por fazer | | |
| F2.3 Checkpoint, tarefas, `INCOMPLETE_READ_SET` | por fazer | | |
| F2.4 Retoma a frio | por fazer | | |
| F2.5 Skills das 6 autoridades + nascimento | por fazer | | |
| F2.6 Coverage (D07), su-confirmed-guard, H2, D09, capture_run | por fazer | | |
| F2.7 Gate | por fazer | | |

## 2. Defeitos do F0 fechados

| ID | Como | Teste |
| --- | --- | --- |
| D08 | `operation.run(read_set=…)`: input só de leitura verificado sob o lock, antes do staging → `STALE_INPUT` | T11_ReadSet |
| D17 | `projection.operational_state`: o modelo é lido com os seus ficheiros declarados como inputs do bootstrap, e o marcador de estado é revalidado depois do modelo. Se mudou, repete; se continuar a mudar, `CONCURRENT_WRITE` | D17_ProjeccaoNumaRevisao |

## 3. Testes adaptados

- `test_audit_findings.F02`: o substituto de `snapshot` aceita o novo argumento `inputs` (mudança de assinatura; a garantia testada não muda).

## 4. Limitações conhecidas

- `MODEL_INPUTS` enumera o que `build_model` lê hoje. Uma leitura nova no dashboard que não se declare aqui fica fora da janela. Mitigação em F2.7: um teste de contrato que compare as leituras do modelo com a lista.
