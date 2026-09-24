# F7 — Relatório da fase (mudanças, migração e compatibilidade)

Estado: **in progress** (2026-09-24). Desenho e decisões Q1–Q4: [DESENHO.md](DESENHO.md). Gate: T35/T36/T41/T42; o rollback preserva a informação nova e bloqueia o downgrade destrutivo.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F7.1 Raio de impacto | integrado | (este) | `library/kernel/tools/impact.py` (só leitura): `edges` (dependências que os artefactos já registam: linha → FC/âmbito/WP/candidato/nó do desenho, FC → WP, candidato → parecer da revisão corrente, unidade de conhecimento → parecer), `stale` (derivado em cada leitura, Q1: `ROW_RESOLVED`, `ROW_WITHDRAWN`, `ROW_MISSING`, `ROW_CHANGED`, `VIA_CONTRACT`, `VIA_CANDIDATE`, `KNOWLEDGE_CHANGED`, com a cadeia; `bytes` = revisão de bytes exacta, informativa; `unverified` = linha citada sem impressão registada), `impact --changed` (raio antes de publicar + citações por texto do `resolve.cited_by`, candidatos). **Impressão por linha** (decisão do mantenedor, 2026-09-24): `functional.py`, `inventory.py`, `review.py` juntam a `based_on`, ao publicar, `shared-understanding.md#<id>` com `row` (`state`, `criticidade`, `resolved`, `retired`) e o seu `sha256`, calculada da SU que o read-set do rascunho fixa. `handoff-contract.md` → *Dependencies*. Matriz F0: 2 entradas. `test_impact.py` 14 casos. Full 109/109, 3018; stdlib 90/90, 2220; ambos exit 0 |
| F7.2 Consumidores | por fazer | | |
| F7.3 Versões suportadas, D10, rollback | por fazer | | |
| F7.4 Docs | por fazer | | |
| F7.5 Relatório e gate | por fazer | | |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F7.0 | levantamento e desenho | precisa do contexto da sessão; o detalhe volta a ser preciso | na sessão |
| F7.1 | motor, publicação, testes | idem | na sessão |

## 3. Testes adaptados

- Nenhum em F7.1: a impressão por linha acrescenta entradas a `based_on`, que nenhum teste existente fixa.

## 4. Limitações conhecidas

- O estado de uma linha é a secção onde está: uma linha com o mesmo id movida para outra secção deixa de ser lida como linha, e os dependentes vêem-na como inexistente (`ROW_MISSING`), não como `ROW_CHANGED`. O resultado para o gate é o mesmo; a mensagem é menos precisa.
- Artefactos publicados antes do F7.1 (incluindo o pacote congelado da F6) não levam impressão por linha: vêem resolvida, retirada e inexistente; estado/criticidade mudados no sítio aparecem como `unverified` até à próxima publicação.
- Os nós do desenho não têm impressão (o desenho é escrito pelo autor, a aprovação fixa o `sha256` do ficheiro): só resolvida, retirada e inexistente.
- `KNOWLEDGE_CHANGED` compara o `sha256` gravado no mandato com o ficheiro actual do repositório; a prova simula a mudança editando o mandato (nenhum teste escreve em `library/`).
