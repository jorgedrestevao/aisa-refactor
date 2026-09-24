# Enquadramento — f8-r5-fx01

> Dono do processo: directora administrativa, Organização Exemplo
> Data: 2026-09-24
> Executor: aisa-start (piloto F8, execução R5, segmento S1)
> Pedido literal: [P1] "Os reembolsos de despesas de deslocação demoram semanas e há queixas todos os meses. Quero saber o que devemos fazer: melhorar o que temos, comprar uma ferramenta ou construir alguma coisa. Preciso de uma recomendação com custos para levar à administração." (pedido.md#P1)

## T1 · actors

O colaborador que se desloca; a chefia directa (aprova abaixo do limiar); a direcção financeira (aprova acima); a contabilidade (processa e paga). Quem manda formalmente: não está escrito, não sei dizer.

## T2 · trigger

Começa quando o colaborador preenche a folha de cálculo por deslocação e envia por email com fotografias dos recibos. Frequência: à volta de 300 pedidos por mês — dito de memória, sem registo visto.

## T3 · activities

O colaborador envia a folha por email; a contabilidade copia os valores para outra folha e depois para o ERP-X; a aprovação acontece algures nesse percurso, conforme o valor.

## T4 · outcomes

Sai o pagamento ao colaborador. Como se sabe que correu bem: não sei dizer.

## T5 · invariants

Recibo digitalizado legível obrigatório — sem recibo, não há reembolso. Limiar de aprovação: a entrevista diz 500€, a política escrita diz 250€ — não sei qual vale, alguém tem de decidir. Taxa por quilómetro: fixada em deliberação da administração que não foi entregue, não a tenho. Comprovativos: conservados pelo prazo legal aplicável, não sei o número de anos.

## T6 · failure_today

Pedidos em duplicado quando o colaborador reenvia o email; recibos ilegíveis; pagamentos atrasados porque o email se perde. Duas pessoas da contabilidade gastam parte do dia nisto, não souberam dizer quantas horas por semana. Quanto custa ao todo: não sei.

## T7 · change_requested

Submissão, aprovação e pagamento de despesas de deslocação. Fora: despesas de representação e adiantamentos.

## Invariantes (M-n)

| id | invariante | o que orienta | fonte |
|----|-----------|----------------|-------|
| M-1 | Recibo digitalizado legível obrigatório — sem recibo, não há reembolso. | elegibilidade do reembolso | declaração do dono do processo, 2026-09-24 |
| M-2 | Limiar de aprovação: a entrevista diz 500€, a política escrita diz 250€ — não sei qual vale, alguém tem de decidir. | quem aprova cada pedido, por valor | declaração do dono do processo, 2026-09-24 |
| M-3 | Taxa por quilómetro: fixada em deliberação da administração que não foi entregue, não a tenho. | cálculo do reembolso em viatura própria | declaração do dono do processo, 2026-09-24 |
| M-4 | Comprovativos: conservados pelo prazo legal aplicável, não sei o número de anos. | prazo de retenção dos comprovativos | declaração do dono do processo, 2026-09-24 |

## Autoridades nomeadas (além do dono)

- Administração — orçamento; taxa por quilómetro.
- Director financeiro — limiar de aprovação acima do valor.
- Compras — confirmar se existem licenças de plataforma low-code no contrato corporativo.

## Regras

Estas invariantes são hipótese do dono do processo, registadas tal como declaradas — nada foi inferido pelo executor. `/frame` confirma ou corrige cada M-n. Nenhum fornecedor ou produto foi nomeado nesta secção.
