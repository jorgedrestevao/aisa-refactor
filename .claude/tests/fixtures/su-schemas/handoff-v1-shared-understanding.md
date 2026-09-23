# Shared Understanding — fx-handoff (sintético)

> Engagement: fx-handoff
> Fase actual: Discovery

<!-- Fixture sintética do schema handoff-v1 (states.md -> Admission of a question).
     Conteúdo derivado de .claude/tests/fixtures/handoff-v1/fx-hv1-02-pp-constrained (E01-E03)
     e fx-hv1-04-headless (E05). Nenhum dado real. -->

## Confirmed

| id | lens | claim | evidência | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|
| C-001 | enquadramento | O dono declara que a plataforma foi decidida pela direcção de sistemas | declaração do dono do processo, 2026-09-23 — answers.md#ROTA | 2026-09-23 | organizacional | R-00 |

## Assumed

| id | lens | claim | base da assumption | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|

## Unknown

| id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-001 | business | Arredonda-se cada linha ao cêntimo ou só o total? | design_choice | funcional, aceitação: três linhas de 0,335 € dão 1,02 € por linha e 1,01 € no total | cálculo do valor do pedido (proposed_to_be) | role: responsável de compras com contabilidade | regra escolhida pelo dono, com o exemplo de limite como teste de aceitação | blocks_scope | Critical | reuniao | dimensionante: (a) arredondar cada linha ao cêntimo (b) arredondar só o total | sources/entrevista-processo.md#C2; sources/entrevista-processo.md#C3 | R-01 |
| U-002 | governance | Qual é o limiar que exige a direcção financeira? | fact_gap | funcional, aceitação: muda o roteamento da aprovação | roteamento da aprovação (observed_as_is) | fonte: despacho da direcção financeira | valor do despacho, com data | blocks_scope | Critical | documento | dimensionante: o valor define quem aprova | sources/entrevista-processo.md#C4; sources/matriz-papeis.md#M4 | R-01 |
| U-003 | user | De que cor é o botão de submeter? | design_choice | nenhum impacto demonstrável | ecrã de submissão | role: equipa de produto | — | — | Low | email | cosmético: (a) azul (b) verde | sources/entrevista-processo.md#C7 | R-01 — estacionada (sem impacto demonstrável; delegada à equipa sem requisito de acessibilidade ou identidade) |
| U-004 | operations | Qual é o limite de pedidos por minuto do ERP-X? | fact_gap | viabilidade, operação: define o ritmo do envio nocturno | envio de pedidos aprovados | fonte: documentação do ERP-X | limite documentado ou medido | implementation_proof | Med | documento | dimensionante: o limite fixa o lote | sources/nota-integracao.md#I4 | R-01 |
| U-005 | data | A cópia do catálogo na folha de compras está desactualizada face ao ERP-X? | fact_gap | funcional | catálogo de equipamento | role: dono de dados | comparação dos preços em vigor | blocks_scope | Med | email | dimensionante | sources/nota-dados.md#D1 | R-01 — estacionada () |

## Conflicted

| id | lens | conflito | partes | impacto | âmbito | quem decide | fecho | bloqueio | criticidade | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|
| X-001 | operations | Quem valida pedidos acima do limiar: direcção ou compras? | matriz de papéis ∧ entrevista | funcional: muda a transição de aprovação | roteamento da aprovação | role: dono do processo | decisão do dono registada | blocks_scope | Critical | sources/matriz-papeis.md#M4; sources/entrevista-processo.md#C4 | R-01 |

## Risky

| id | lens | risco | impacto | mitigação proposta | ronda |
|---|---|---|---|---|---|
| R-001 | operations | Janela de manutenção do ERP-X coincide com o envio | envio falha e repete | reagendar fora da janela | R-01 |
