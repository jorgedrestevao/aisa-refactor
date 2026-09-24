# Chairman Synthesis — Round O-02 / Phase Options

## Personas heard
- solution-architect (autor técnico, inline) — candidato publicado (`_design/candidates.json` rev.2)
- architecture-review (REV-0006)
- data-integration (REV-0007)
- security-operation (REV-0008)
- ux-process (REV-0009)
- cost-estimate (REV-0010)

## Overlaps → strengthened
- "C-006/C-007 têm de ser revalidados na SU antes de tratar O-006 como base para /blueprint" — anchored by data-integration (REV-0007.F01, `blocking`) e architecture-review (REV-0006.F06, ângulo de premise_refs) → A-007 (was C-007), A-008 (was C-006).
- "TW-4 (decisions.md#D-002) está calibrado ao limiar antigo (5000€) e não cobre a faixa 3000-5000€ introduzida por X3" — anchored independentemente por architecture-review (REV-0006.F01, `blocking`) e security-operation (REV-0008.F01, `blocking`) → registado como precondição de O-006 em `options.md`, não uma linha SU nova (o objecto do achado é `decisions.md#D-002`, fora do que esta fase escreve).
- "O mecanismo que impõe o total/arredondamento e o gate M-2 tem de ser transaccional e síncrono, nunca por rollup ou só no fluxo" — anchored por data-integration (REV-0007.F02/F03, ambos `blocking`) e security-operation (REV-0008.F02, `material`, ângulo da plane de enforcement) → U-017 (Unknown, design_choice, criticidade Critical).
- "Suporte nativo ao arredondamento meio-para-o-par não está confirmado" — anchored por architecture-review (REV-0006.F02), data-integration (REV-0007.F02/F05, com verificação directa de `craft/powerfx.md`/`craft/flow-craft.md`) e cost-estimate (REV-0010.F04) → U-015 (Unknown, fact_gap).
- "A interacção X1×X3 sobre o mesmo campo Total nunca foi testada perto da fronteira dos 3 000€, e o critério de aceitação financeiro do UAT precisa de ser reescrito" — anchored por architecture-review (REV-0006.F03), ux-process (REV-0009.F02/F03) e cost-estimate (REV-0010.F02/F03, um deles `blocking`) → U-016 (Unknown, proof_obligation).

## Gaps → carried as Assumed/Unknown
- "A ordem de grandeza de O-006 está marcada `unavailable`, mas o modelo do pacote tem linhas ao grão certo para os componentes que o delta toca" — proposto só por cost-estimate (REV-0010.F01) → não gera linha SU (é uma correcção ao candidato, não uma pergunta ao dono); verificado nesta síntese contra `estimation-model.md` EFFORT TABLE e projectado em `options.md#Recommendation` como banda contingente (0,5–1d nativo / 3,5–4d com plug-in).

## Contradictions → Conflicted
- (nenhuma) — os cinco pareceres não se contradizem entre si; `review.py show-reviews` → `divergences: []`. Convergência forte nos quatro pontos acima, por caminhos independentes — tratada como reforço, nunca como divergência.

## Admissão de perguntas

- U-015 — "O Power Platform tem função nativa para arredondamento meio-para-o-par, ou exige lógica explícita/plug-in?" — admitida — tipo: fact_gap — impacto: solucao, viabilidade — por preencher: — (todos os campos preenchidos a partir de REV-0006.F02, REV-0007.F02/F05 — verificação directa de `craft/powerfx.md`/`craft/flow-craft.md`, sem função de arredondamento documentada além de `formatNumber` — e REV-0010.F04).
- U-016 — "O caso de fronteira X1×X3 foi testado, e o critério de aceitação financeiro foi reescrito para a regra nova?" — admitida — tipo: proof_obligation — impacto: aceitacao — por preencher: — (campos a partir de REV-0006.F03, REV-0009.F02/F03, REV-0010.F02/F03).
- U-017 — "O mecanismo de escrita do Pedido/Linhas impõe o total/arredondamento de forma transaccional, nunca por rollup, de modo a que o gate M-2 seja fiável?" — admitida — tipo: design_choice — impacto: solucao, aceitacao — por preencher: — (campos a partir de REV-0007.F02/F03, REV-0008.F02; criticidade Critical porque a falha deste mecanismo é uma violação silenciosa de M-2, regra que nenhum candidato pode quebrar).
- REV-0006.F01 / REV-0008.F01 (TW-4 desactualizado) — não escrito como Unknown novo: o objecto do achado é `decisions.md#D-002` (uma condição de revisão já registada), não um facto ou escolha da SU — registado como precondição de O-006 em `options.md`, disposição `delegated` (dono do processo, antes de /decide).
- REV-0006.F04 (verificação manual dos impact_refs) — não escrita como Unknown: é uma limitação de processo (a rota `change-impact` foi recusada pelo motor), não uma pergunta ao dono — disposição `delegated` ao coordenador/autor técnico.
- REV-0006.F05 / REV-0009.F01 (nomear os campos afectados por X1) — não escritas como Unknown: são detalhe de desenho a resolver em `/blueprint --refresh` — disposição `delegated` ao autor técnico.
- REV-0006.F06 — não escrita como Unknown separada: o mesmo achado que gera A-007/A-008 (ver Overlaps) — disposição `accepted`.
- REV-0007.F04/F05/F06/F07/F08 (sequência IVA/arredondamento; anti-padrão formatNumber; tolerância de R-004; U-012 em falta em premise_refs; colisão de rótulos X1-3 vs X-001) — não escritas como Unknown: são correcções de detalhe do candidato ou orientações de implementação, todas com um dono e um momento de fecho nomeados — disposição `delegated` ao autor técnico.
- REV-0008.F03 (U-006 regista o limiar em vigor por pedido) — não escrita como Unknown nova: é um requisito a incorporar quando U-006 (já existente) for desenhado — disposição `delegated` ao autor técnico, em /blueprint.
- REV-0009.F04/F05/F07 (erro amigável se plug-in; menções a "5000€" desactualizadas; U-002 cobrir elemento novo) — não escritas como Unknown: detalhe de desenho ou condicional a uma pergunta já existente — disposição `delegated`.
- REV-0009.F06 (mandato ux-process para candidato model-driven só recebeu craft de Canvas — `screen-patterns.md` é o único ficheiro de craft de ecrã do pacote e declara-se `Canvas standard components only`) — não escrita como Unknown: é uma lacuna do **pacote** (nenhum craft model-driven equivalente existe), não um facto ou escolha deste engagement — disposição `deferred`, impacto registado; **findings pendentes**, único item em `open_findings`.

## Risks captured
- (nenhum risco novo) — R-003, R-004, U-011, U-013 herdados de O-002 sem alteração; o agravamento da materialidade de X-001 pelo limiar mais baixo é mencionado em `options.md` como consequência de X-001 (já Conflicted), não como uma nova linha Risky.

## SU rows written this round
- A-007 (was C-007) — arredondamento passa a linha-a-linha, meio-para-o-par (mudancas.md ¶1); Assumed, não Confirmed — autoria da nota não corresponde a papel nomeado (mesmo padrão de A-006/was C-003).
- A-008 (was C-006) — limiar da direcção financeira desce para 3 000 € (mudancas.md ¶3); Assumed, mesma razão que A-007.
- U-015 — suporte nativo ao arredondamento meio-para-o-par (fact_gap).
- U-016 — caso de fronteira X1×X3 + critério de aceitação financeiro do UAT (proof_obligation).
- U-017 — mecanismo transaccional de escrita do Pedido/Linhas para o gate M-2 (design_choice, criticidade Critical).

## Phase artefact written
- `options.md` — 1 candidato activo (O-006, delta sobre D-002/O-002); O-002 retirado; O-001/O-003/O-004/O-005 mantidos sem delta. Terminal: decision blocked por precondições (TW-4, U-015, U-016, U-017), não por alternativa concorrente.

## Class coverage — round O-02
- `DO-NOTHING` — O-005 (sem delta nesta ronda; herdado de O-01)
- `PROCESS-CHANGE` — O-004 (sem delta nesta ronda; herdado de O-01)

## Concern coverage — round O-02
- C1 (Need, value, existing capability) — D0 — não material nesta ronda: nenhuma reavaliação da necessidade ou da capacidade existente foi pedida (reabertura é sobre regras, não sobre a decisão de construir).
- C2 (Functional and process fit) — D2: revisto por data-integration e architecture-review — a regra de cálculo (arredondamento, C-005/A-007) e o routing de aprovação (M-2/A-008) são o próprio objecto da reabertura; gap — sequência exacta IVA/arredondamento por linha ainda por fixar (REV-0007.F04).
- C3 (User and experience fit) — D1: revisto por ux-process (REV-0009) — gaps: campo de valor de linha por nomear no ecrã, critério de aceitação financeiro por reescrever (U-016), mandato assente em craft de Canvas para um candidato model-driven (REV-0009.F06, `deferred`).
- C4 (Data and information fit) — D2: revisto por data-integration (REV-0007) — achados `blocking` sobre imposição server-side e mecanismo transaccional (U-017); C-005/A-007 (sequência de cálculo) ainda por fixar.
- C5 (Integration and ecosystem fit) — D0 — não material nesta ronda: a reabertura não toca a integração com o ERP-X (U-004/U-012 inalterados, herdados).
- C6 (Security, privacy and control) — D2: revisto por security-operation (REV-0008) — achado `blocking` sobre TW-4 desactualizado face à faixa 3000-5000€, que agrava directamente X-001 (ainda Conflicted); enforcement plane do gate M-2 (U-017) partilhado com C4.
- C7 (Governance, authority and compliance) — D1: TW-4 (decisions.md#D-002) e X-001 tratados como precondição/risco existente, não reabertos como decisão nova — fecham por `/decide`/`/revisit`, fora desta ronda.
- C8 (Lifecycle, ALM and change) — D0 — não material aqui, herdado de O-01 (nenhum sinal de ALM nesta ronda).
- C9 (Scale, performance and resilience) — D0 — não material aqui, herdado de O-01 (U-001 continua Low, sem sinal de escala elevada).
- C10 (Operability, support and ownership) — D0 — não material aqui, herdado de O-01.
- C11 (Economics, entitlement and TCO) — D2: revisto por cost-estimate (REV-0010) — achado material sobre a ordem de grandeza marcada `unavailable` quando o modelo tem linhas ao grão certo (REV-0010.F01); banda contingente publicada em `options.md#Recommendation` (0,5–1d / 3,5–4d, `estimation-model.md` EFFORT TABLE), candidato por corrigir na próxima revisão.
- C12 (Strategic fit, reversibility and dependency) — D1: revisto por architecture-review (REV-0006) — reversibilidade de O-006 confirmada igual a O-002 (o delta não muda plataforma nem forma); dependência nova: TW-4/U-015/U-017 como precondições explícitas de fecho.

## Per-option long form

### O-006 — O-002 actualizado — arredondamento linha-a-linha e limiar 3 000 €   ·   Delta sobre decisão adoptada (change-impact, na prática — rota do engagement mantida `platform-constrained`)   ·   Power Apps (model-driven) + Dataverse + Power Automate
- **Anchored by**: solution-architect; architecture-review; data-integration; security-operation; ux-process; cost-estimate
- **Scope**: whole solution (herdado de O-002, C-008)
- **Viability**: viable with preconditions
- **Outcome**: intervenção tecnológica viável dentro da plataforma imposta (C-001), delta sobre D-002, condicional a quatro precondições novas (TW-4, U-015, U-016, U-017) mais as quatro herdadas de O-002 (U-002/U-013, U-006, U-011, U-012)
- **High-level architecture**: idêntica a O-002 (Pedido, Linha de pedido, Registo de aprovação, Catálogo condicional a U-004; ecrãs gerados pela shell orientada a registos); dois componentes mudam — a regra de arredondamento desloca-se de uma coluna calculada no cabeçalho (Pedido) para uma nova coluna calculada na Linha de pedido, com a fórmula de agregação do total revista (X1); o valor de comparação do gate M-2 muda de 5 000 € para 3 000 € (X3) — mesma regra de negócio, valor novo
- **Assumptions**: A-001, A-002 (herdadas); A-007 (was C-007 — nova regra de arredondamento, Assumed); A-008 (was C-006 — novo limiar, Assumed) — ambas dependentes de confirmação directa da contabilidade/direcção financeira, ainda por obter
- **Order of magnitude**: candidato declara `ORDER OF MAGNITUDE UNAVAILABLE` (REV-0010.F01, achado material — o modelo do pacote não é limitado a construções inteiras como o candidato assume); verificado nesta síntese contra `estimation-model.md` EFFORT TABLE (Dataverse): Calculated/rollup column 0,25d, Business rule 0,5d, Low-code plugin 3d — banda contingente publicada em `options.md`: **0,5–1 dia** (2 colunas calculadas ajustadas + regra de negócio do limiar) se U-015 resolver nativo; **3,5–4 dias** se exigir plug-in síncrono. `PACK MODEL`, banda deste candidato apenas
- **Material strengths**: preserva toda a base de segurança/auditoria/dados já decidida em D-002; nenhuma das três mudanças de `mudancas.md` altera plataforma, forma ou âmbito
- **Disqualifiers**: (none)
- **Preconditions**: TW-4 (`decisions.md#D-002`) reescrito para 3 000 € ou reconfirmado pelo dono — director de sistemas de informação — antes de `/decide` (REV-0006.F01, REV-0008.F01); suporte nativo ao arredondamento confirmado, ou plug-in síncrono decidido — autor técnico/fonte: documentação Power Platform — antes de `/blueprint` (U-015); mecanismo transaccional de escrita nomeado — autor técnico — antes de fechar o routing M-2 (U-017); caso de fronteira + critério de aceitação financeiro reescrito — direcção financeira — antes de `/decide` (U-016); as quatro precondições herdadas de O-002 continuam de pé, inalteradas
- **Material trade-offs**: nenhum novo — mesmo forfeit de acesso móvel de O-002 (U-002/U-013)
- **Material risks**: R-003, R-004, U-011, U-013 (herdados); materialidade de X-001 agravada pelo limiar mais baixo (mais pedidos urgentes na faixa sujeita a aprovação financeira) — risco existente, não uma linha nova
- **Cost drivers**: 2 colunas calculadas (arredondamento por linha + total revisto); regra de negócio do limiar (valor); contingência de plug-in síncrono se U-015 resolver não-nativo (driver dominante, +3d)
- **Reversibility**: alta — igual a O-002 (mesma loja, mesma forma); o delta é sobre regras de negócio, não sobre arquitectura
- **Revision condition**: se U-015 resolver para plug-in síncrono E o orçamento/prazo não o comportarem, reconsiderar se a regra de arredondamento pode ser simplificada (confirmar com a contabilidade se meio-para-cima linha-a-linha, sem meio-para-o-par, seria aceitável)
- **Decision-changing uncertainties**: U-015 (custo: spike técnico); U-017 (custo: desenho em /blueprint); U-016 (custo: caso de teste + sign-off da direcção financeira); TW-4 (custo: decisão do dono, sem esforço técnico)
- **Proof requirement**: bounded pilot (mesma UAT de O-002) + caso de teste de fronteira dedicado (U-016)
- **Concern notes**: C4/C6 são os que mais pesam nesta ronda — o mecanismo transaccional (U-017) decide se o gate M-2 continua fiável depois do delta; C11 tem banda real disponível, não publicada no candidato (REV-0010.F01)

### O-001, O-003, O-004, O-005 — sem delta nesta ronda
Registo completo mantido em `lens-outputs/chairman-synthesis-O-01.md#Per-option-long-form`; não repetido aqui — nenhum revisor nem o autor técnico propôs alteração a nenhum dos quatro nesta ronda.

## Parser warnings (if any)
- (none) — os 5 pareceres chegaram, após correcção, no contrato completo (`input_revision`, `coverage`, `assumptions`, `unanswered`, `recommended_actions`, `sources_used`, e `evidence`/`failure_scenario` por achado).
