# F7 — Desenho das mudanças, da migração e da compatibilidade

Plano: `../plan/05_FASES.md` F7; `../plan/07_MIGRACAO.md`; `../plan/06_VALIDACAO.md` T35, T36, T41, T42. Gate: T35/T36/T41/T42; o rollback preserva a informação nova e bloqueia o downgrade destrutivo.

Objectivo: suportar a evolução real sem refazer tudo nem perder conhecimento.

Estado: **proposta** — as decisões Q1–Q5 vão ao mantenedor antes de qualquer código.

## Ponto de partida (levantamento, 2026-09-24)

| Tema | O que já existe | Lacuna para a F7 |
| --- | --- | --- |
| Impacto de uma mudança | `resolve.impact_of`/`cited_by`: citação por texto + sucessores no grafo, **candidatos, não veredicto**. `/answer` passo 7: grep e juízo por dependente, «sem grafo de dependências» | Os artefactos da F4–F6 já registam dependências **estruturadas** por id (FC → linhas da SU em `requirement_refs`/`open_refs`; WP → FC; âmbito → linhas/FC; candidatos → `premise_refs`/`source_refs`; desenho → `su_refs`). Ninguém as lê em conjunto. Um FC que cita uma linha entretanto resolvida (`resolved →`) continua com autorização `current`: a impressão do item não mudou (T41 falha hoje) |
| Mudança só editorial | `graph.drift`: `state`, `criticidade`, `resolved` divergentes bloqueiam, texto informa (`GATE_FIELDS`). Coverage: dependência do grafo só pelo subconjunto consumido (C04/C05). Mandato: `knowledge_refs` com `sha256` só das unidades listadas | Não há prova T42 ponta a ponta sobre os artefactos da F4–F6 |
| Versão suportada | `SCHEMA_UNSUPPORTED` em `workflow` (estado), `functional`, `inventory`, `review` (candidatos). T36 provado na F1 com o código histórico real (`ba0c27b`) | `handoff-index`, pareceres, mandatos, registo de disposições: sem verificação de versão uniforme; nenhuma tabela única do que é suportado |
| Migração | `migrate.py` (`dry-run` · `apply` · `restore` · `init`) recusa legado (F1, opção A). Nenhum engagement handoff-v1 real existe (rollout passo 1) | **D10** (F0): `restore --force` escreve por cima do trabalho posterior à migração, incluindo `D-NNN` novos — downgrade destrutivo |
| Rollback de código | Artefactos da F4–F6 são ficheiros novos, aditivos | Não provado que código anterior (fim da F5) sobre um engagement da F6 deixa os artefactos novos intactos |
| Docs | — | `ARCHITECTURE.md`, `ONBOARDING.md` desactualizados desde a F5; não há doc de setup/manutenção/recuperação/backup |

## Decisões para o mantenedor

| # | Decisão | Recomendação | Alternativa |
| --- | --- | --- | --- |
| Q1 | Onde vive o «stale» estrutural (T41) | **Derivado em cada leitura** por um motor só de leitura `impact.py`, a partir das dependências que os artefactos já registam e do estado das linhas. Nenhum booleano escrito (como o coverage §10: não diverge das fontes) | Marcar `stale` dentro dos artefactos (escrita nova, pode divergir) |
| Q2 | O que é mudança semântica de uma linha da SU (T41/T42) | **Os campos que já bloqueiam no grafo**: `state`, `criticidade`, `resolved` (inclui `withdraw` e transição `was X`). Texto editado no sítio = editorial, informa (o contrato já obriga um facto mudado a entrar como linha nova com `was`). `verificado_em` renovado não é mudança | Qualquer mudança de texto conta (reabre de mais: falha T42) |
| Q3 | Efeito de uma dependência stale | **Bloqueia a versão final**: `render_gate`, `scope_gate` e a prontidão do `release` recusam FC/WP/âmbito que dependem de linha resolvida ou retirada; o rascunho continua. Sai do bloqueio republicando o dependente com a referência nova (a autorização segue a impressão do item, como hoje) | Só aviso (um pacote «pronto» pode assentar numa premissa morta) |
| Q4 | Migração, dado a opção A (sem classic) | **Sem migração nova**: T35 continua não aplicável (sem consumidor — plano: «não construir suporte sem consumidor»). A F7 faz: tabela única de versões suportadas aplicada a todos os leitores dos artefactos (T36 alargado); **D10** — `restore` perde o `--force`: com trabalho posterior recusa sempre e diz o que mudou; prova de rollback de código com o código real do fim da F5 sobre um engagement da F6 | Subir `handoff-state` para `/2` e migrar 1→2 como caminho exercitado (suporte sem consumidor real) |
| Q5 | Docs do item 5 | **Um doc novo `docs/OPERACAO.md`** (setup, manutenção, recuperação, acesso e backup) + actualizar `ARCHITECTURE.md` e `ONBOARDING.md` ao estado da F6 | Só actualizar os existentes |

## 0. Subagentes e paralelismo — avaliados antes de definidos

Critério: README → *Regras de execução*; `library/kernel/orchestration.md` → *When a subagent is justified*.

| Uso em F7 | Precisa do contexto de quem lança? | O detalhe volta a ser preciso? | Veredicto |
| --- | --- | --- | --- |
| `impact.py`, guarda de versões, D10, testes | sim: contratos da F1–F6 | sim: é o produto | **inline** |
| Prova de rollback com código histórico | — (execução determinística numa árvore de trabalho) | — | **código**, sem agente |
| Actualização de docs | sim: o que mudou em cada fase | sim | **inline** |
| Revisão independente | nenhum julgamento novo no runtime: o impacto é determinístico; o julgamento por dependente de texto livre continua no `/answer` passo 7 | — | **nenhum agente novo** |

## 1. Raio de impacto e stale transitivo (Q1–Q3; T41, T42)

`library/kernel/tools/impact.py` (só leitura):

- `edges(eng)`: as dependências registadas — linha → FC (`requirement_refs`, `open_refs`), linha/FC → âmbito (`includes`/`excludes`), FC → WP (`realizes`), obrigação de prova → WP (`proves`), linha → candidato (`premise_refs`, `source_refs`), linha → desenho (`su_refs`), candidato → parecer (revisão), WP → estimativa/spec (citação + revisão do inventário, já em `trace.derived_check`).
- `stale(eng)`: dependentes de uma linha com `resolved`, retirada, ou com `state`/`criticidade` diferentes do que o dependente citou. Transitivo: FC stale → WP que o realizam → estimativa/spec → release. Cada achado diz a cadeia (`C-003 resolvida → C-010 · FC-0002 · WP-0003`).
- `impact(eng, changed)`: o raio de uma mudança antes de a publicar (o `/answer` mostra-o no passo 7; o texto livre continua por grep e juízo, candidatos).
- Mudança editorial: nenhuma entrada; a revisão de bytes (`based_on.sha256`) continua exacta e é reportada como «bytes mudaram, sem mudança semântica».

Consumidores (Q3): `functional.render_gate`, `trace.scope_gate`, `release.readiness`, `projection`/`/status`.

## 2. Versões suportadas e rollback (Q4; T35, T36)

- `workflow.SUPPORTED`: uma tabela `artefacto → schema_version aceite`. Todos os leitores dos artefactos handoff (estado, FC, âmbito, inventário, candidatos, pareceres, mandatos, registo, índice do release) recusam uma versão fora da tabela com `SCHEMA_UNSUPPORTED`, sem tocar no ficheiro.
- D10: `migrate.restore` sem `--force`. Com trabalho posterior: `WORK_AFTER`, lista o que mudou, nada se escreve (plano 07: «não automatizar restore sobre engagement activo»).
- Rollback de código: o teste extrai o código do fim da F5 (`56cb4e1`) e corre as suas escritas (publicação da SU e das decisões) num engagement com artefactos da F6; `_design/scope.json`, `_design/work-packages.json` e `_release/` ficam byte a byte.
- T35: não aplicável por decisão (opção A); a recusa segura é o T03 da F1.

## 3. Docs (Q5)

`docs/OPERACAO.md`: instalar e correr as suites; manter (o que é administrativo em `library/`); recuperar (`operation recover`, pendências, `bootstrap`); acesso e backup (quem guarda `projects/<slug>/`, o que nunca se edita à mão, releases imutáveis). `ARCHITECTURE.md` e `ONBOARDING.md`: motores da F4–F6, agentes actuais, sem personas.

## 4. Incrementos

| Inc. | Trabalho | Prova |
| --- | --- | --- |
| F7.1 | `impact.py` (`edges`, `stale`, `impact`) + contrato | T41, T42 (motor) |
| F7.2 | Consumidores: gates de render, âmbito e release; `/answer` passo 7; `/status` | T41 ponta a ponta na fixture fx-hv1-02 |
| F7.3 | `workflow.SUPPORTED` em todos os leitores; D10; prova de rollback com o código da F5 | T36 alargado; rollback |
| F7.4 | Docs | leitura cruzada com o código |
| F7.5 | Relatório e gate | T35/T36/T41/T42 |
