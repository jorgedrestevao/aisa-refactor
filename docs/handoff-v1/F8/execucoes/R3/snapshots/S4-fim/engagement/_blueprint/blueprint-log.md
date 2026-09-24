# Blueprint log — f8-r3-fx02

Uma linha por versão. Append-only.

## v01 — 2026-09-24T13:20:00Z

- **Trigger**: inicial (primeira versão, sem `--option`; produzida em Decision, D-002).
- **SU ids consumidos**: C-001, C-002, C-003, C-004, C-005, C-006, C-007, C-008, M-1, M-2, M-3, M-4, D-001, D-002, A-001..A-005, U-001, U-002, U-004, U-006, U-007, U-008, U-009, U-010, U-011, U-012, U-013, X-001, R-003, R-004.
- **Architecture entry gate**: outcome classe 2 (fit with constraints), selected solution PP-containing (Power Apps model-driven + Dataverse) → `authorization: authorized` (architecture-templates/README.md §2/§4). Scope: whole solution.
- **Reconciliação (passo 1e)**: `_coverage/coverage_v04.json` (stage=reconciliation) — 83/83 unidades revistas, `coverage: gaps` (13 lacunas encaminhadas, todas com `required_action`+`responsible_role`), `eligible: true`. Publicada antes de desenhar.
- **Violações de cap (screen-consolidation-rules.md)**: nenhuma — PedidoFormScreen com 2 entidades escritas (Pedido, LinhaPedido) ≤ 3; ≤12 campos editáveis visíveis; ≤5 acções.
- **Estrutura (`--blueprint-check`)**: `valid: yes (0 block, 14 warn)`. Os 14 avisos são todos `BP-BAD-ID` sobre `su_refs` que citam `M-1`..`M-4` (invariantes do enquadramento) — o `ID_RE` do motor (partilhado com `coverage.py`) não inclui o prefixo `M`; achado de ferramenta, não defeito do desenho — as quatro invariantes existem como linhas SU (`shared-understanding.md#M-1`..`#M-4`). Sinalizado, não corrigido por esta via (fora do âmbito de `/blueprint`).
- **`open_architecture_choices`**: 2. Estrutural (bloqueia aprovação): autoridade/mecanismo de integração do `ItemCatalogo` (U-004/U-012). Não estrutural: dimensionamento de entitlement (U-011).
- **Revalidação cruzada de campo (passo 11b)**: não aplicável — primeira versão, sem versão anterior para comparar.

## v01 — tentativas de fecho pós-produção (2026-09-24T13:35:00Z)

- Perguntados directamente ao dono: U-012 (interface ERP-X), U-004 (tempo real vs cópia), U-011 (entitlement). Respostas literais: "não sei" às três (council-log.md). Nenhuma fecha — nenhuma base A/B/C disponível (fact ≠ fit).
- `open_architecture_choices[0]` (autoridade do catálogo, U-004/U-012) — **continua estrutural e em aberto**. Bloqueia a aprovação desta versão (blueprint-contract.md hard rule 5); não bloqueia a produção, que já aconteceu.
- Cobertura da versão (etapa blueprint, revisões `_coverage/coverage_v07.json`..`v09.json`, a mais recente e válida `v09`): `coverage: gaps`, `eligible: false` — "Há obrigações por cobrir ou por fundamentar; a versão pode continuar em discussão, mas não se anuncia pronta para aprovação." 7 obrigações por fundamentar (U-002, U-004, U-011, U-012, U-013, R-004 contingente, e a própria escolha estrutural do catálogo); 8 excluídas do âmbito deste registo com autoridade (D-002: U-001/U-007/U-008/U-009/U-010 — obrigações financeiras/de negócio, não de arquitectura; D-001: X-001 — condição deslocada para antes da entrega final, não do blueprint; D-002: R-001/R-002 — anomalia superseded).
- **Aprovação do desenho (passo 15) não pedida nesta ronda**: a etapa (ii) do portão (cobertura) recusa-a mecanicamente, sem override disponível para uma escolha estrutural por natureza técnica. Passos 15b (âmbito da entrega), 16 (autorização de contratos funcionais) e 17 (inventário de trabalho) dependem todos dessa aprovação e ficam, por isso, também bloqueados nesta ronda.
