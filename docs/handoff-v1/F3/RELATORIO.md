# F3 — Relatório da fase (análise integrada e materialidade funcional)

Estado: **in progress** (2026-09-23). Desenho e decisões Q1–Q5: [DESENHO.md](DESENHO.md). Gate: T05–T08, T18, T19 e a fixture `fx-hv1-02` (§6 do desenho).

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F3.1 Etapa `lens` no coverage + contrato | integrado | (este) | `coverage.py`: quarta etapa, sem alvo como a `reconciliation` (`TARGETLESS`); `lens_coverage` com as seis dimensões, `conflict_scan` e autor; regras fixas em `_check_lens`; revisão por dimensão em `_check_lens_semantic` (revisor ≠ autor); `lens_skeleton` (herda perspectivas, nunca a revisão); `lens_round_state`; CLI `lens-draft` e `round-state` (exit 0 fecha, 4 não fecha); secção «Perspectivas» no relatório. Contrato `coverage-contract.md` §4.8, tabela de etapas e de raiz. `test_coverage_lens.py` 21 casos (T18, T19 parte fixa e veredicto do revisor, T07). Full 87/87 ficheiros, 2820 testes; stdlib 68/68, 2022; ambos exit 0 |
| F3.2 `lens-checklists.md` + retirada das 6 skills de lente | por fazer | | |
| F3.3 `/round` integrado + revisor + fecho por cobertura | por fazer | | |
| F3.4 `/frame` integrado + revisor; hooks de fase por perfil | por fazer | | |
| F3.5 Captura PM-U, `/status`, fixture `fx-hv1-02` | por fazer | | |
| F3.6 Relatório e gate | por fazer | | |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F3.1 | motor, contrato, testes | precisa do contexto da sessão (decisões Q1–Q5, motor de F2); o detalhe volta a ser preciso | na sessão |

## 3. Testes adaptados

- `test_audit_round2.R2_05` (manter): toda a chamada a `compute_basis` declara `graph_consumed`. O esqueleto `lens` passa `graph_consumed=()`, porque a etapa não consome o grafo. É uma declaração explícita, não uma excepção ao teste.

## 4. Limitações conhecidas

- A regra fixa da T19 prova que cada referência resolve (linha da SU que existe, `answers.md#…`, `enquadramento.md#…`, ficheiro em `_capture/` ou `inputs/`). Não prova que a linha citada trata a perspectiva. Isso fica para o revisor independente (`semantic_review.dimensions`). Sem revisão, a passagem fecha «por rever».
- A regra «revisor ≠ autor» compara nomes declarados (`performed_by.name` ≠ `lens_coverage.author.name`). Não prova que a sessão do revisor não tinha o contexto do autor. Isso vem das instruções do `/round` (F3.3).
- Ambiente: o contentor reiniciado perdeu `openpyxl` e `cffi`. Instalados de `requirements-dev.txt` e com `pip install cffi` antes da corrida. Não houve mudança de código.
