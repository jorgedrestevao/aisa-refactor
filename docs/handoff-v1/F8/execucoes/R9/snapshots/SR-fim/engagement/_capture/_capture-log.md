# Capture log

| timestamp | layer | file | event | detail |
|---|---|---|---|---|
| 2026-09-24T10:30:38 | LT | pedido.md | extracted | paragraphs 5, headings 1, table_lines 0, sha256 a7da9323 |
| 2026-09-24T10:30:39 | LT | entrevista-processo.md | extracted | paragraphs 7, headings 1, table_lines 0, sha256 8a709386 |
| 2026-09-24T10:30:39 | LT | matriz-papeis.md | extracted | paragraphs 5, headings 1, table_lines 0, sha256 be7ebaa5 |
| 2026-09-24T10:30:39 | LT | nota-dados.md | extracted | paragraphs 3, headings 1, table_lines 0, sha256 990dc582 |
| 2026-09-24T10:32:05 | LT | evidence-index.md | indexed | 4 sources — not captured 4 |
| 2026-09-24T10:32:47 | LT | pedido.md | extracted | paragraphs 5, headings 1, table_lines 0, sha256 a7da9323 |
| 2026-09-24T10:32:47 | LT | entrevista-processo.md | extracted | paragraphs 7, headings 1, table_lines 0, sha256 8a709386 |
| 2026-09-24T10:32:47 | LT | matriz-papeis.md | extracted | paragraphs 5, headings 1, table_lines 0, sha256 be7ebaa5 |
| 2026-09-24T10:32:47 | LT | nota-dados.md | extracted | paragraphs 3, headings 1, table_lines 0, sha256 990dc582 |
| 2026-09-24T10:32:50 | LT | evidence-index.md | indexed | 4 sources — ok 4 |
| 2026-09-24T10:33:04 | L2 | process-model.md | generated | run 1 \| files: pedido.md, entrevista-processo.md, matriz-papeis.md, nota-dados.md \| sources: pedido.md USED · entrevista-processo.md USED · matriz-papeis.md USED · nota-dados.md USED |
| 2026-09-24T13:35:51 | LT | nota-urgentes.md | extracted | paragraphs 3, headings 1, table_lines 0, sha256 44e9eab9 |
| 2026-09-24T13:35:57 | LT | evidence-index.md | indexed | 5 sources — ok 5 |
| 2026-09-24T13:40:00 | L2 | process-model.md | generated | run 2 \| files: pedido.md, entrevista-processo.md, matriz-papeis.md, nota-dados.md, nota-urgentes.md \| sources: pedido.md USED · entrevista-processo.md USED · matriz-papeis.md USED · nota-dados.md USED · nota-urgentes.md USED \| PM-U new: PM-U-007 |
| 2026-09-24T16:33:40 | LT | mudancas.md | extracted | paragraphs 3, headings 1, table_lines 0, sha256 eba5ccb7 |
| 2026-09-24T16:33:46 | LT | evidence-index.md | indexed | 6 sources — ok 6 |
| 2026-09-24T16:35:00 | L2 | process-model.md | generated | run 3 \| files: pedido.md, entrevista-processo.md, matriz-papeis.md, nota-dados.md, nota-urgentes.md, mudancas.md \| sources: pedido.md CHECKED · entrevista-processo.md CHECKED · matriz-papeis.md CHECKED · nota-dados.md CHECKED · nota-urgentes.md CHECKED · mudancas.md USED \| PM-U retired: PM-U-001 (arredondamento — respondido por X1, mudancas.md ¶1, substitui C-007), PM-U-002 (limiar — respondido por X3, mudancas.md ¶3, substitui C-006) |
| 2026-09-24T16:36:00 | check | coverage.py --stage reconciliation | reported | freshness: stale (pré-existente, antes desta captura) — acção: produzir/rever blueprint; não corrigido aqui (fora do âmbito de `/capture`) |
