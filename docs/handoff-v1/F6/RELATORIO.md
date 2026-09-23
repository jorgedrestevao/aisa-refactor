# F6 — Relatório da fase (rastreabilidade completa e handoff implementável)

Estado: **in progress** (2026-09-23). Desenho e decisões Q1–Q8: [DESENHO.md](DESENHO.md). Gate: T31–T34, T37–T40; zero requisito material órfão no âmbito entregue; esforço por WP coerente; pacote parcial nunca apresentado como completo.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F6.1 Âmbito e inventário | integrado | (este) | `library/kernel/tools/inventory.py` (`draft` · `check` · `publish` · `show`, `--kind scope\|work-packages`) pelo coordenador, com histórico imutável; schemas `handoff-scope/1` e `handoff-work-packages/1`. Integridade: ids, revisão, incluídos que resolvem (SU, jornadas de FC), exclusão só com `D-NNN` que existe (T33, parte do motor), WP com FC e nós do desenho resolvidos pelo resolvedor de selectores do `coverage.py` (um nó exacto), `proves` só obrigações de prova, dependências sem ciclo, nenhum campo de esforço (Q2). Lacunas visíveis: âmbito sem autorização, WP sem `realizes`/`acceptance`/DoD. `handoff-contract.md` → *Work packages and completeness*. Matriz F0: 5 entradas. `test_inventory.py` 13 casos. Full 102/102, 2950; stdlib 83/83, 2152; ambos exit 0 |
| F6.2 Rastreabilidade | por fazer | | |
| F6.3 Estimativa, gate de âmbito, N2/N3/S6 | por fazer | | |
| F6.4 Templates | por fazer | | |
| F6.5 Release, segredos, aceitação | por fazer | | |
| F6.6 Percursos e 3.º ensaio T43 | por fazer | | |
| F6.7 Relatório e gate | por fazer | | |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F6.0 | levantamento e desenho | precisa do contexto da sessão; o detalhe volta a ser preciso | na sessão |
| F6.1 | motor, schemas, testes | idem | na sessão |

## 3. Testes adaptados

- Nenhum em F6.1.

## 4. Limitações conhecidas

- Uma referência a um nó do desenho por índice (`proof_obligations[0]`) resolve, mas move-se se a lista for reordenada; o contrato do coverage (§5.1) pede o `sha256` do alvo nesse caso, e o inventário ainda não o guarda.
