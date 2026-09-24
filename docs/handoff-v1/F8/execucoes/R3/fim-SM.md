# FIM DE SEGMENTO F8 — R3 / SM

**feito:**
- Copiada `inputs/nota-urgentes.md` (nota do responsável de compras, 2026-10-01, sobre o caminho de urgência).
- `/capture`: run 2 — extração de texto (LT) da nota nova, índice de evidência regenerado (5 fontes), `process-model.md` regenerado (nota USED; nova pergunta do modelo de processo `PM-U-007` sobre o mecanismo de suspensão).
- `/answer --revalidate C-003`: o facto mudou (prazo "mesmo dia" → "fim do dia útil seguinte" + regra de suspensão nova) → transição normal, não revalidação simples. Nova linha **A-006** (Assumed — resposta de terceiro, sem autoridade nomeada na linha original), `C-003` marcada `resolved -> A-006`.
- Raio de impacto (`impact.py --changed C-003`): 2 dependentes estruturais no blueprint v01 (`entities[Pedido]`, `screens[PedidoFormScreen]`, ambos via `su_refs`); texto citando C-003 em `_blueprint/ux-blueprint_v01.yaml`, `_synthesis/as-is.md`, `_synthesis/risks-and-assumptions.md`; `decisions.md`/`options.md` não citam C-003 diretamente — `(none)`.
- Republicado o que depende do facto: `_synthesis/as-is.md` e `_synthesis/risks-and-assumptions.md` reescritos (C-003 → A-006, nota do novo prazo, X-001 ainda sem resposta desta nota); `_synthesis-log.md` com as duas entradas.
- Admitida **U-014** (design_choice, TO-BE DIVERGENCE) promovendo `PM-U-007` a pergunta formal da SU: o que "suspende a encomenda" significa mecanicamente.
- `/blueprint --refresh`: **não produzido** — bloqueado no portão de reconciliação (passo 1e). Ver anomalia 1.
- Confirmação pedida ao cliente sobre A-006 e U-014: ambas voltaram "não sei / por confirmar".

**estado:** fase `decision`, rota `platform-constrained`, ronda `D-01`.
Publicado nesta sessão: SU (`A-006` was `C-003`; `U-014` nova) · `answers.md#C-003` · `council-log.md` (5 entradas) · `_capture/process-model.md` run 2 · `_capture/_capture-log.md` · `_capture/evidence-index.md` · `_synthesis/as-is.md`, `_synthesis/risks-and-assumptions.md`, `_synthesis-log.md` · `_coverage/coverage_v10.json` .. `coverage_v13.json` (etapa reconciliation; v13 é a última, mas inelegível — ver anomalia 1). `decisions.md`, `options.md`, `_blueprint/ux-blueprint_v01.yaml` **não tocados** (blueprint v02 não chegou a ser produzido).

**perguntas abertas e bloqueios:**
- A-006 por confirmar pelo dono — resposta do cliente: "ainda não sei — fica por confirmar".
- U-014 por responder pelo responsável de compras — resposta do cliente: "não sei — fica por confirmar".
- Blueprint v01 continua a versão vigente, desactualizado face a A-006 no caminho de urgência (entidade Pedido, ecrã PedidoFormScreen) — `/blueprint --refresh` fica pendente, bloqueado (anomalia 1).
- Bloqueios já existentes, não tocados por este segmento: X-001 (Critical, ainda sem resposta), U-006/U-007/U-011/U-012 (condições de D-002 por fechar), sponsor confirmation de D-002 (pending).

**próximo passo que o aisa indica:** corrigido o bloqueio de cobertura (anomalia 1) → `/blueprint --refresh` para produzir a v02; entretanto `/status` para a agenda completa.

**anomalias (literais):**
1. **Auto-infligida, agora permanente no histórico de `_coverage/`.** Ao reconstruir a revisão de reconciliação (passo 1e de `/blueprint`, exigido antes de qualquer versão nova), o executor escreveu por engano um item de cobertura (`cov-026`) com `requirement_refs: ["PM-U-007"]` — um id do motor de captura, não da SU/decisions. `coverage.py` recusa **sempre** esse ref (`COV-DEAD-REF`), **independentemente da `disposition`** (o teste de existência corre antes de qualquer lógica de `retire`/`excluded`). Ao mesmo tempo, `coverage.py` exige que **toda** identidade de obrigação que apareceu nalguma revisão publicada anterior reapareça em todas as seguintes, com disposição (`COV-UNREVIEWED` se desaparecer). As duas regras juntas tornam este id **impossível de corrigir de forma limpa**: reaparecer dispara `COV-DEAD-REF`; desaparecer dispara `COV-UNREVIEWED`. Resultado: `coverage_v13.json` (a mais recente) fica com `contract_validity: valid`, `freshness: current`, mas `eligible: false` para sempre, por esta única razão — as restantes ~24 obrigações estão correctamente tratadas. A causa raiz foi corrigida (a pergunta foi admitida como `U-014`, própria da SU), mas o registo antigo não se apaga (append-only, por desenho). **Isto bloqueia `/blueprint --refresh`** no passo 1e, que não cobre este caso explicitamente (só nomeia `COV-NO-REVIEW`/`COV-STALE`) — o executor parou aqui em vez de inventar um contorno. Recomendação registada ao mantenedor do motor: `coverage.py` devia deixar `disposition: retire` dispensar o teste de existência do próprio `requirement_ref` que está a retirar (é exactamente o caso que a `retire` existe para cobrir).
2. Já conhecida de sessão anterior, confirmada de novo: `R-001`/`R-002` continuam com `resolved: false` embora `R-003`/`R-004` as citem como `was` — não corrigido aqui (fora do âmbito deste segmento), registado outra vez em `cov-023`.
