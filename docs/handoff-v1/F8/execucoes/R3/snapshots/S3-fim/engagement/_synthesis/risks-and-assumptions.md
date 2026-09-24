# Risks and Assumptions — f8-r3-fx02

## Assumptions to validate during build

- A-001 — o impacto declarado (pedidos duplicados, divergências de arredondamento) é qualitativo, sem medição de frequência ou custo. Base: relato do responsável de compras, sem números (entrevista-processo.md · ¶3, ¶6). Validar: quem — responsável de compras/financeiro; por quando — não nomeado. `verificado_em`: 2026-09-24; `validade`: organizacional. Aceite como base da decisão (D-002), sem ser testada primeiro.
- A-002 — o requerente precisa de confirmação visível de que o pedido foi recebido, para não reenviar por dúvida — causa observada dos pedidos duplicados. Base: inferência razoável a partir de "acha que o email não chegou" (entrevista-processo.md · ¶6). Validar: junto de uma amostra de requerentes. `verificado_em`: 2026-09-24; `validade`: organizacional. Aceite como base da decisão (D-002).
- A-003 — hoje não existe um sistema único de registo dos pedidos — vivem dispersos entre email e a folha de cálculo de compras. Base: nota-dados.md · ¶2; entrevista-processo.md · ¶1. `verificado_em`: 2026-09-24; `validade`: organizacional.
- A-004 — o custo de não fazer nada é qualitativo, sem valor monetário medido. Base: entrevista-processo.md · ¶3, ¶6. `verificado_em`: 2026-09-24; `validade`: organizacional.
- A-005 — a fórmula do custo as-is está escrita (volume × tempo por passo × taxa horária carregada + custo dos duplicados + custo das divergências), mas nenhum dos três factores está medido (U-001, U-009, U-010). `verificado_em`: 2026-09-24; `validade`: organizacional.

## Accepted risks (with mitigations)

- R-003 (was R-001) — pedidos duplicados por reenvio; a correspondência difusa descrita não é idempotente nas escritas Web API/fluxo (corrida TOCTOU). Mitigação registada: nomear mecanismo exacto antes do blueprint (regra activada nas escritas, ou verificação+criação atómica num plug-in síncrono/custom API em transacção), testado em UAT com submissão concorrente. Trigger de revisão: TW-2 (D-002) — se a auditoria/licenciamento reprovar.
- R-004 (was R-002) — cópia local do catálogo de preços como anti-padrão de cache, se U-004 resolver para cópia própria; sem dono, cadência ou deteção de drift, reproduz o mesmo risco de hoje. Mitigação registada: se U-004 → cópia local, exigir dono de reconciliação, cadência e deteção de drift diferente de contagem de linhas.
- U-011 — entitlement/licenciamento das 5 populações para a loja de dados governada da plataforma imposta (C-001) ainda não confirmado; aceite como risco de D-002. Trigger: TW-3 (D-002) — se se confirmar que faltam licenças.
- U-013 — instalabilidade/licenciamento da app nativa móvel para o forfeit de O-002, condicional a U-002, ainda não confirmado; aceite como risco de D-002. Trigger: TW-1 (D-002) — se se confirmar necessidade de acesso móvel.

## Unresolved Unknowns (Critical)

Nenhuma. A única Unknown que teve criticidade Critical (U-005, valor do limiar financeiro) já foi respondida e promovida a Confirmed (C-006).

## Conflicts still on the table

- X-001 (Critical, governance∧operations) — o caminho de urgência (C-003: compras encomenda primeiro, chefia valida no mesmo dia) não diz se também salta a aprovação da direcção financeira quando o valor ultrapassa o limiar do despacho (M-2). Lado operações: a via existe para velocidade em avarias que impedem trabalhar. Lado governança: M-2 foi declarado invariável pelo próprio dono. Nenhuma fonte resolve nas duas direcções (council-log.md, passagens 1 e 2 de Discovery); o dono respondeu "não sei; não tenho essa informação" quando questionado directamente. Fecha só por decisão do dono (`/answer X-001 "..."`). Passou para Decision em aberto, com a condição explícita (D-001 override; reforçada em D-002/TW-4) de fechar antes de qualquer entrega final que dela dependa.

## Expired validity — re-verification obligations

Nenhuma. Todas as linhas Confirmed e Assumed do engagement estão dentro da validade declarada nesta data (2026-09-24).

## Conditions and preconditions the decision recorded

- Mecanismo de auditoria desenhado e confirmado (U-006) — owner: role: director de sistemas de informação / role: auditoria interna — funded? not named — by when: antes do /blueprint fechar.
- Entitlement/licenciamento das 5 populações confirmado (U-011) — owner: role: director de sistemas de informação — funded? not named — by when: not named.
- Interface do ERP-X confirmada, para U-004 (U-012) — owner: role: director de sistemas de informação / fonte: ERP-X — funded? not named — by when: antes de fechar U-004.
- Confirmar que o acesso não é predominantemente móvel, ou que a app nativa é instalável/licenciada (U-002, U-013) — owner: role: director de sistemas de informação — funded? not named — by when: not named (o dono respondeu "não sei" a U-002 nesta ronda).
- Precondition (o que tem de ser verdade antes do trabalho arrancar): as quatro condições acima; nenhuma adicional nomeada pelas fontes.

Nenhuma destas está satisfeita — todas continuam por fechar à data desta síntese.

## Proof obligations

- Claim: viabilidade do mecanismo de duplicados e da base de segurança/auditoria de O-002 · Level: not named · Method: bounded pilot (mesma UAT de O-001), com submissão concorrente do mesmo conteúdo · Owner: role: director de sistemas de informação · Funded?: não avaliado.

## Watch-list summary

- TW-1 (U-002 — SU) — se se confirmar que o pedido tem de ser feito a partir de telemóvel ou fora do escritório → rever para O-001.
- TW-2 (U-006/U-011 — SU) — se a auditoria reprovar o mecanismo de registo → rever a opção.
- TW-3 (U-011 — SU) — se se confirmar que as licenças necessárias não estão disponíveis → rever a opção.
- TW-4 (X-001, M-2/C-006 — SU; proposto pelo premortem.md) — se chegar um pedido urgente acima do limiar de 5 000€ antes de X-001 fechar → travar o processamento automático, forçar aprovação manual.
