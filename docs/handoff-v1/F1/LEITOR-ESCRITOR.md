# F1 — Tabela leitor/escritor/schema e alterações incompatíveis

Estado em `90d77a0` (fim do F1.6). Plano: `../plan/05_FASES.md` F1, item 7.

**Leitura das colunas:**
- **Escritor** é quem pode escrever o dado, e como.
- **Guarda** é o que recusa uma escrita fora desse caminho.
- **Versão histórica** é `jorgedrestevao/aisa@85baf10`, cuja árvore é igual a `ba0c27b` neste repositório.

## 1. Dados e schemas

| Dado | Schema / versão | Escritor | Leitores | Guarda | Versão histórica |
| --- | --- | --- | --- | --- | --- |
| Bloco `workflow` em `_state.json` | `handoff-state/1` (`library/kernel/schemas/`) | `/start`, uma vez, no nascimento (passo 7). A seguir, só o `workflow.py` pelo coordenador; a mudança de rota fica para F5. | `workflow.py` (`profile_of`, `validate_profile`), `bootstrap.py`, `operation.py`, `migrate.py`, `pre-profile-check.py`, `pre-authority-guard.py` | `pre-authority-guard` recusa escrita por ferramenta que mude o bloco ou retire chaves de `_state.json`, incluindo o `.tmp` | Ignora o campo, mas não chega a escrever: o grafo 2 bloqueia-a |
| Ausência do bloco `workflow` | — (legado) | versão histórica | igual à linha anterior | Recusa em todas as camadas; a leitura continua | É o formato dela |
| `_graph/meta.json` `schema_version` | inteiro 2 (engagements `handoff-v1`); 1 = versão histórica | `graph.py` via coordenador (`migrate.init`, `resolve`, `on-su-mirror`) | `graph.read`, `bootstrap`, `projection`, `dashboard` | `pre-authority-guard` recusa sempre escrita por ferramenta em `_graph/` | Lê só 1: recusa escrever em engagements novos (T36, com código real) |
| Capacidades do pack | `handoff-pack/1` | autoria do pack (`library/`, por commit) | `workflow.pack_capabilities` | — | Não as lê |
| Colunas da admissão (Unknown, Conflicted) | colunas da SU (`states.md` → *Schema*) | 6 lentes, `chairman-synthesis`, `/answer`, `/start` (cabeçalho) | `dashboard.parse_su` (único parser), `arbiter_declarations`, `resolve`, `bootstrap` | `pre-authority-guard` (prontidão; `Confirmed` sem localizador) | Não as conhece. Um engagement novo é recusado antes de chegar a elas |
| Marca `— estacionada (<motivo>)` | marca na última coluna | escritor da linha, árbitro, chairman | `parse_su` (não aberta, não fechada), `round_delta.estacionadas` | Sem motivo, não conta e sai diagnóstico | Lê-a como texto |
| Linha `Confirmed` | limiar de `states.md` | escritores da SU | idem | `pre-authority-guard` recusa uma nova ou mudada sem localizador válido (`handoff-v1`) | Só avisava depois de escrever, e só ids `C-` novos |
| `_work/checkpoint.json` | `handoff-work/1` | coordenador (F2) | retoma (F2) | Escrita por ferramenta em `_work/` sempre recusada | — |
| `_design/functional-contracts.json` | `handoff-functional/1` | coordenador (F5) | blueprint, spec, testes (F5) | Escrita por ferramenta em `_design/` sempre recusada | — |
| Índice de entrega | `handoff-index/1` | projecção (F6) | destinatário (F6) | — | — |
| Resposta estruturada | `handoff-response/1` | `workflow.response` | skills, hooks | — | — |
| `_migration/` | — | `migrate.py` via coordenador | `migrate.py` | Escrita por ferramenta sempre recusada (D05) | Guardava só `_graph/` e `_ops/` |
| Modelo do dashboard | `schema` 3 (motor 1.15.0) | `dashboard.py` | `/status`, `/round` 5f, `dashboard.html` | — | Schema 2 |

## 2. Alterações incompatíveis

| # | Alteração | Quem sente | Tratamento |
| --- | --- | --- | --- |
| 1 | Grafo `schema_version = 2` nos engagements novos | Versão histórica aberta sobre um engagement novo | Intencional (Q1): recusa pelos guardas dela; teste T36 com o código de `ba0c27b` |
| 2 | Engagement sem bloco `workflow` passa a só leitura | Engagements existentes | Opção A: continuam na versão histórica; aqui lêem-se (`/status`, dashboard) |
| 3 | `/start` pergunta perfil e rota; recusa pack sem capacidade | Quem cria engagements | Q5; os packs skeleton não declaram `handoff-v1` |
| 4 | Escrita por ferramenta em `_graph/`, `_ops/`, `_migration/`, `_work/`, `_design/` sempre recusada | Edição à mão | Antes só com bootstrap por pronto (D05). `AISA_GUARD_MODE=log` é o override |
| 5 | `_state.json` não perde chaves nem muda `workflow` por ferramenta | Skills que reescrevem o JSON inteiro | Guardado também no `.tmp` |
| 6 | Admissão P-26 substituída pela `handoff-v1`; colunas novas na SU; marcador `TO-BE DIVERGENCE` retirado | Lentes, chairman, árbitro, testes | Q3/Q4; linhas antigas nunca reclassificadas; testes adaptados no mesmo commit |
| 7 | O árbitro estaciona (com motivo) em vez de baixar swing e criticidade | `/round` 5f | A sexta edição sancionada mudou (`states.md`) |
| 8 | `Confirmed` sem localizador é recusado em `handoff-v1` | Chairman, lentes | Antes avisava. Integridade fecha; princípio 5 do `CLAUDE.md` actualizado |
| 9 | Modelo do dashboard `schema` 3; chaves P-26 do `arbiter` removidas | Leitores do modelo | Nenhum consumidor exige 2 (verificado) |
| 10 | `/status`, `/resume` e `aisa-orient` deixam de escrever a linha de saúde | Quem lia a linha na SU | Q6 (D02); a saúde vem do motor em cada leitura |
| 11 | Pack PP 1.10.0 | Testes de versão do pack | Emendados com entrada no changelog |
| 12 | SCOPE-STATEMENT v2 | Documentação | Q4; 8 cópias |
| 13 | Scaffolds de teste precisam do bloco `workflow` | Quem escreve testes de motor | `fixtures/handoff-v1/estado.py` |

## 3. Limitações conhecidas

- Escritas por `Bash` (`mv` do `.tmp`, heredoc) não passam por hooks, na versão nova e na histórica. A garantia completa é o coordenador para todas as escritas canónicas (F2).
- O hook de Skill não adivinha entre vários engagements montados sem nome. As outras camadas recusam a escrita.
- Até F4, o gate de `/options` conta ≥ 3 opções em todas as rotas. Nas rotas `platform-constrained` e `change-impact`, esse aviso lê-se contra a regra de `phases.md`.
