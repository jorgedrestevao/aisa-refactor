# Shared Understanding — fx-hv1-02

> Fase actual: Discovery
> Última actualização: 2026-09-23

## Confirmed

| id | lens | claim | evidência | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|
| C-001 | enquadramento | Âmbito: pedido, aprovação e passagem a compras | pedido.md#¶4 | 2026-09-23 | organizacional | R-00 |
| C-002 | business | O valor do pedido é a soma de quantidade × preço unitário por linha, mais IVA | entrevista-processo.md#¶2 | 2026-09-23 | organizacional | R-01 |
| C-003 | operations | Pedidos urgentes seguem para compras e a chefia valida no mesmo dia | entrevista-processo.md#¶5 | 2026-09-23 | organizacional | R-01 |
| C-004 | governance | A chefia nunca aprova um pedido feito por si própria | matriz-papeis.md#¶2 | 2026-09-23 | organizacional | R-01 |
| C-005 | user | Requerente cria e consulta os seus pedidos | matriz-papeis.md#¶1 | 2026-09-23 | organizacional | R-01 |

## Assumed

| id | lens | claim | base da assumption | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|
| A-001 | operations | A chefia valida os urgentes no próprio dia útil | entrevista-processo.md#¶5 (inferido: «no mesmo dia») | 2026-09-23 | organizacional | R-01 |

## Unknown

| id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-001 | financial | Arredonda-se cada linha ao cêntimo ou só o total? | design_choice | funcional, aceitação: três linhas de 0,335 € dão 1,02 € por linha e 1,01 € no total | cálculo do valor do pedido (proposed_to_be) | role: responsável de compras com contabilidade | regra escolhida pelo dono, com o exemplo de limite como teste de aceitação | blocks_scope | Critical | reuniao | dimensionante: (a) arredondar cada linha ao cêntimo (b) arredondar só o total | entrevista-processo.md#¶2; entrevista-processo.md#¶3 | R-01 |
| U-002 | data | Qual é o limiar que exige a direcção financeira? | fact_gap | funcional, aceitação: muda o roteamento da aprovação | roteamento da aprovação (observed_as_is) | fonte: despacho da direcção financeira | valor do despacho, com data | blocks_scope | Critical | documento | dimensionante: o valor define quem aprova | entrevista-processo.md#¶4; matriz-papeis.md#¶4 | R-01 |
| U-003 | user | O botão de submeter deve ser verde? | design_choice | — | ecrã de submissão | role: requerente | — | none | Low | email | cosmético: (a) verde (b) outra cor | entrevista-processo.md#¶7 | R-01 — estacionada (R-01: sem impacto demonstrável) |

## Conflicted

| id | lens | conflito | partes | impacto | âmbito | quem decide | fecho | bloqueio | criticidade | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Risky

| id | lens | risco | impacto | mitigação proposta | ronda |
|---|---|---|---|---|---|
