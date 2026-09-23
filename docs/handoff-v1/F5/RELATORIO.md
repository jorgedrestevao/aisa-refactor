# F5 — Relatório da fase (candidatos comuns, especialistas e primeiro percurso vertical)

Estado: **in progress** (2026-09-23). Desenho e decisões Q1–Q6: [DESENHO.md](DESENHO.md). Gate: T25–T30 e o primeiro ensaio T43; revisões na versão certa; zero confirmação por maioria; handoff incompleto rotulado.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F5.1 Candidatos publicados por rota | integrado | (este) | `library/kernel/tools/review.py` (candidatos: `draft-candidates`, `check-candidates`, `publish-candidates`, `show-candidates`) pelo coordenador, com histórico imutável; schema `handoff-candidates/1`. Integridade: ids, revisão, rota do engagement, premissas na SU; regras por rota — plataforma imposta com `imposition_ref` = autoridade da rota, nenhum candidato fora dela, sem mínimo (T27); `solution-choice` < 3 só com motivo; `change-impact` com baseline e delta. Lacunas visíveis (ordem de grandeza sem fonte, arquitectura, reversibilidade). Rascunhos abertos listados (para T25). `handoff-contract.md` → *Options candidates*. Matriz F0: 3 entradas. `test_review_candidates.py` 10 casos. Full 97/97, 2908; stdlib 78/78, 2110; ambos exit 0 |
| F5.2 Router e mandatos | por fazer | | |
| F5.3 Pareceres, disposições, dialéctica | por fazer | | |
| F5.4 `/options` por rota, `specialist-reviewer`, personas, `/retro` | por fazer | | |
| F5.5 Percurso vertical e ensaio T43 | por fazer | | |
| F5.6 Relatório e gate | por fazer | | |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F5.0 | levantamento e desenho | precisa do contexto da sessão; o detalhe volta a ser preciso | na sessão |
| F5.1 | motor, schema, testes | idem | na sessão |

## 3. Testes adaptados

- Nenhum em F5.1.

## 4. Limitações conhecidas

- A plataforma imposta é declarada no conjunto de candidatos (`imposed_platform`), e o motor exige que a imposição cite a autoridade da rota; o `_state.json` não guarda o nome da plataforma. A comparação é por nome normalizado (maiúsculas/minúsculas e espaços), não por identidade de produto.
