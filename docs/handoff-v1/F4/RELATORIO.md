# F4 — Relatório da fase (autoria funcional e primeiro desenho coerente)

Estado: **in progress** (2026-09-23). Desenho e decisões Q1–Q6: [DESENHO.md](DESENHO.md). Gate: T20–T24; o render recusa preencher uma regra em falta; referência ou aprovação desactualizada bloqueia a publicação final.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F4.1 `functional.py` + completude | integrado | (este) | `library/kernel/tools/functional.py`: `draft`, `check`, `publish`, `show`. Publica pelo coordenador numa operação: a revisão corrente e a cópia imutável em `_design/history/`. A integridade recusa com `INTEGRITY_FAILURE` (schema, ids nunca reutilizados nem largados fora de `retired_ids`, revisão +1, referências a SU, `D-` e desenho que resolvem, desenho de opção recusado). A frescura vem antes da integridade (`STALE_INPUT`). Um replay devolve o mesmo recibo. A completude dá `BLOCKING_GAP` sem recusar: essenciais, cálculo sem unidades, arredondamento ou os três tipos de exemplo, delegação incompleta, pergunta bloqueante aberta. Schema aditivo sem mudar de versão. `handoff-contract.md` descreve o motor e corrige a tabela F1 (FC em F4, pelo plano 05). Matriz F0: 3 entradas. `test_functional_contracts.py` 19 casos (T20). Full 91/91, 2863; stdlib 72/72, 2065; ambos exit 0 |
| F4.2 Autorização | por fazer | | |
| F4.3 Coerência desenho ↔ FC | por fazer | | |
| F4.4 Passo funcional do `/blueprint` + `fc-reviewer` | por fazer | | |
| F4.5 Render | por fazer | | |
| F4.6 Percurso, relatório e gate | por fazer | | |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F4.0 | levantamento e desenho | precisa do contexto da sessão (plano, contratos, motores); o detalhe volta a ser preciso | na sessão |
| F4.1 | motor, schema, testes | idem | na sessão |

## 3. Testes adaptados

- Nenhum em F4.1.

## 4. Limitações conhecidas

- A completude verifica a presença dos campos essenciais, não a sua qualidade: uma `rule` escrita mas errada passa. Isso é do `fc-reviewer` (F4.4) e do dono (F4.2).
- «Cálculo» é declarado pelo autor (campo `calculation`); o motor não deduz que um FC calcula. Um cálculo não declarado escapa à exigência de arredondamento e dos três exemplos — é achado do revisor.
