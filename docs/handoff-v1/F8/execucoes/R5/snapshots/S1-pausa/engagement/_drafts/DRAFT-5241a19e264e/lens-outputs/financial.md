## R-01 — financial

**What matters**

`context.json.funding_gate = true` (o dono declarou que avançar depende de aprovação orçamental de terceiros) — confirmado de forma independente pela nota de TI: não existe orçamento aprovado para este projecto, e qualquer custo recorrente precisa de aprovação da administração (C-009). Isto activa o envelope orçamental/modelo de financiamento como pergunta legítima, mas nenhuma das fontes ainda dá um número: nem o custo actual do processo (horas × taxa), nem a taxa por quilómetro em vigor.

**Tensions / risks**

Não é possível escrever o baseline de custo actual (volume × tempo de ciclo × taxa) como `Assumed` porque falta o próprio input do tempo: a contabilidade não soube dizer quantas horas por semana gasta nisto (U-006) — sem isso não há baseline para bater, e a directora administrativa pediu explicitamente "uma recomendação com custos". A taxa por quilómetro em vigor não foi entregue (U-007, cruza com M-3) — sem ela, a fórmula de reembolso em viatura própria não se valida. Uma suspeita de licenciamento low-code já pago no contrato corporativo (U-008) pode mudar qual opção é mais barata em Options, mas ainda não está confirmada.

**Open evidence**

- ADOPT `constraint: sem orçamento aprovado` → C-009
- ADOPT `custo actual: horas e valor` → U-006
- ADOPT `invariant: taxa-km` → U-007
- ADOPT `constraint: licenciamento por confirmar` → U-008
