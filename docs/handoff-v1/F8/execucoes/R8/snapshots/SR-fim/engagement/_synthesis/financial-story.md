# Financial Story — f8-r3-fx02

> **Economia de decisão apenas.** Este pacote responde a *vale a pena escolher esta opção?* — não a
> *quanto trabalho dá o caminho escolhido?*. Essa segunda pergunta pertence à entrega `estimate`, que é
> a dona semântica do cálculo. Nenhuma figura de esforço de implementação nasce aqui.

## As-is cost baseline

O custo do processo actual está escrito na forma, não no número (A-005): volume de pedidos × tempo perdido por pedido × taxa horária carregada + custo dos pedidos duplicados + custo das divergências de arredondamento com a contabilidade. Nenhum dos três factores estruturais está medido — volume (U-001), tempo por passo (U-009), taxa horária carregada (U-010) — pelo que o envelope fica sem valor monetário à data desta síntese (`verificado_em`: 2026-09-24; `validade`: organizacional, sujeita a revisão quando os três factores fecharem).

## Cost of doing nothing

Qualitativo, sem valor monetário medido (A-004): inclui encomendas duplicadas e divergências de arredondamento com a contabilidade, já observadas como eventos reais mesmo sem contagem (lens-outputs/business.md (primeira passagem de Discovery)).

## Budget envelope and funding

Não declarado. `context.json.funding_gate` não foi respondido pelo dono ("não sei; não foi falado") e, por omissão, as quatro perguntas de financiamento (envelope, CAPEX/OPEX, modelo, limiares) ficam activas (lens-outputs/financial.md (primeira passagem de Discovery)) — U-007, ainda aberta, sem resposta nesta ronda.

## Economic attractiveness of the chosen option

A ronda de Options não produziu uma comparação económica formal entre O-001/O-002 — nenhuma recomendação foi dada entre os dois (options.md#Recommendation: "no recommendation — U-002 decide entre O-001 e O-002"). O dono escolheu O-002 (D-002) citando o custo mais baixo da ordem de grandeza (30–38 dias vs 40–50 dias de O-001, `PACK MODEL`) como razão suficiente, dado que o acesso móvel extra de O-001 não está confirmado como necessário (U-002). A revisão de custo especializada (cost-estimate, REV-0005) registou um achado material ainda por resolver: o multiplicador de complexidade aplicado às duas ordens de grandeza não está justificado pela contagem de entidades do próprio modelo do pacote (REV-0005.F01) — a banda fica por rever pelo autor técnico, não por esta síntese. `COMPARATOR EVIDENCE ABSENT` entre O-004/O-005 e os candidatos construídos: nenhum modelo de esforço comparável foi calculado para eles (options.md#Comparator status).

## Entitlement and cost drivers

- Entitlement/licenciamento das 5 populações (requerente, chefia, compras, direcção financeira, auditoria interna) para a loja de dados governada da plataforma imposta (C-001) — ainda por confirmar (U-011); se o ambiente gerido exigir entitlement premium para toda a população, o custo muda e pode mudar a viabilidade económica do candidato escolhido, não só o preço (chairman-synthesis-O-01.md).
- Integração com o ERP-X para leitura de preços — driver de custo, dependente de U-004/U-012 ainda por fechar.
- Segurança por papel e mecanismo de auditoria (U-006) — driver de custo, a desenhar antes do blueprint.
- Ecrãs gerados pela shell orientada a registos (O-002) são um driver de custo menor que os ecrãs canvas desenhados (O-001) — mesma base de dados e segurança.

## Payback / ROI

Não registado. Sem o envelope de custo as-is quantificado (A-005 com U-001/U-009/U-010 em aberto) nem o critério de sucesso do projecto decidido (U-008), não há hoje uma base para calcular payback ou ROI — a ausência é honesta, não uma omissão.

## Sensitivity and revision triggers

- TW-3 (D-002) — se se confirmar que faltam as licenças necessárias (U-011), rever a opção: a viabilidade económica, não só o custo, pode mudar.
- TW-2 (D-002) — se a auditoria reprovar o mecanismo de registo (U-006/U-011), rever a opção.
- TW-1 (D-002) — se se confirmar necessidade de acesso móvel (U-002), rever para O-001 (custo mais alto).

## Investment reference

Estimativa ainda não produzida — ver a entrega `estimate`.
