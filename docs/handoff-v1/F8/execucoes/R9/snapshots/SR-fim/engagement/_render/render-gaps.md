# Render gaps — f8-r3-fx02

> Append-only. Uma entrada por lacuna encontrada num `/render`. Lacuna, nunca facto inventado
> para a fechar (`.claude/skills/aisa-render/SKILL.md` → *Hard rules* 2).

## Corrida 2026-09-24T14:00:00Z — `/render --all` (v01 de cada deliverable)

| deliverable | slot / secção | razão | owner | acção |
|---|---|---|---|---|
| discovery-report | `solution_name` (required slot) | Nenhuma fonte não-proibida nomeia o projecto: `context.json` só tem `literal_request`; `shared-understanding.md` não tem linha de nome; `decisions.md#D-NNN` é fonte proibida para este deliverable (pré-decisão por construção). Renderizado como `⚠️ missing: solution_name` no título. | evidence | nomear o projecto (uma frase curta) e registá-la em `context.json` ou como linha `Confirmed` da SU |
| solution-blueprint | A4.3 — Caminhos de acesso delegation-safe | não registado nesta versão do desenho (`_blueprint/ux-blueprint_v01.yaml`) | architecture | nomear, por caminho de acesso, o que é delegation-safe contra a loja seleccionada, em `/blueprint --refresh` |
| solution-blueprint | A4.4 — Distribuição | não registado (modelo de partilha, concessão de acesso, o que acontece a um utilizador que muda de papel) | architecture | nomear em `/blueprint --refresh` |
| solution-blueprint | A8 — Ambientes, governação e topologia de release | não registado (ambientes, vinculação de residência, plano de política, rota(s) de release) | architecture | nomear em `/blueprint --refresh` |
| solution-blueprint | A9 — Escolhas irreversíveis e saída | não registado (tipo de propriedade, publisher, região/residência, custo de saída) | architecture | nomear em `/blueprint --refresh` |
| solution-blueprint | A10 — Operabilidade, suporte e modelo de operação | não registado (papel/identidade/mecanismo/alerta/recuperação por caminho de falha; rota de suporte) — a **ausência do próprio modelo de operação**, não apenas um operador sem nome | architecture | desenhar o modelo de operação em `/blueprint --refresh` |

**Nota (§8.2, todas as três correntes)**: a revisão de reconciliação/blueprint a montante que cada
deliverable consome (`_coverage/coverage_v13.json` para discovery-report/executive-report;
`_coverage/coverage_v09.json` para solution-blueprint) tem `coverage: gaps` e, no caso do
blueprint, `freshness: stale` — nenhuma delas está fechada. Nenhum documento desta corrida se
anuncia como completo (ver `render-log.md`).
