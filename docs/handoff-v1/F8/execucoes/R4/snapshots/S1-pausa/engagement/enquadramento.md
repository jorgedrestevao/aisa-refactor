# Enquadramento — f8-r4-fx01

> Dono do pedido: directora administrativa (Organização Exemplo)
> Data: 2026-09-24
> Executor: sessão piloto aisa (handoff-v1, programa F8, execução R4)
> Pedido literal: «Os reembolsos de despesas de deslocação demoram semanas e há queixas todos os meses. Quero saber o que devemos fazer: melhorar o que temos, comprar uma ferramenta ou construir alguma coisa. Preciso de uma recomendação com custos para levar à administração.» (pedido.md#P1) — âmbito: submissão, aprovação e pagamento de despesas de deslocação dos colaboradores; fora: despesas de representação e adiantamentos (pedido.md#P2).

## T1 · actors

O colaborador que se desloca; a chefia directa, que aprova abaixo do limiar; a direcção financeira, que aprova acima; a contabilidade, que processa e paga. Quem manda formalmente no processo: não está escrito, não se sabe dizer. (responsável de contabilidade — entrevista-financas.md#F3)

## T2 · trigger

Começa quando o colaborador preenche a folha de cálculo por deslocação e envia por email com fotografias dos recibos. Frequência: à volta de 300 pedidos por mês — valor dito de memória, sem registo mostrado. (responsável de contabilidade — entrevista-financas.md#F1, #F2)

## T3 · activities

O colaborador envia a folha por email; a contabilidade copia os valores para outra folha e depois para o ERP-X; a aprovação acontece algures nesse percurso, conforme o valor do pedido. (responsável de contabilidade — entrevista-financas.md#F1)

## T4 · outcomes

Sai o pagamento ao colaborador. Como se sabe que correu bem: não se sabe dizer. (responsável de contabilidade — entrevista-financas.md#F1)

## T5 · invariants

Todos os pedidos têm de ter recibo digitalizado legível; sem recibo, não há reembolso. Acima de 500 euros por pedido tem de aprovar o director financeiro, abaixo chega a chefia directa — mas a política escrita diz 250, não 500, e não se sabe qual valor está em vigor. A taxa por quilómetro está fixada em deliberação própria da administração, que a contabilidade não tem. Os comprovativos conservam-se pelo prazo legal aplicável — o número de anos não é conhecido de quem respondeu. (responsável de contabilidade — politica-rh.md#R2, entrevista-financas.md#F3, politica-rh.md#R1, politica-rh.md#R3, politica-rh.md#R4; lido de volta e confirmado tal qual, sem correcções)

## T6 · failure_today

Pedidos em duplicado quando o colaborador reenvia o email; recibos ilegíveis; pagamentos atrasados porque o email se perde. Duas pessoas da contabilidade gastam parte do dia nisto — quantas horas por semana, não souberam dizer. Quanto custa ao todo: não se sabe. (responsável de contabilidade — entrevista-financas.md#F4, #F5)

## T7 · change_requested

Submissão, aprovação e pagamento de despesas de deslocação dos colaboradores. Fora: despesas de representação e adiantamentos. (directora administrativa — pedido.md#P2)

| id | invariante | o que orienta | fonte |
|----|-----------|----------------|-------|
| M-1 | Todos os pedidos têm de ter recibo digitalizado legível; sem recibo, não há reembolso. | condição de aceitação de qualquer pedido de reembolso | T5 |
| M-2 | Acima de 500 euros por pedido tem de aprovar o director financeiro, abaixo chega a chefia directa — mas a política escrita diz 250, não 500, e não se sabe qual valor está em vigor. | regra de aprovação / fluxo de decisão | T5 |
| M-3 | A taxa por quilómetro está fixada em deliberação própria da administração, que a contabilidade não tem. | cálculo do valor a reembolsar em viatura própria | T5 |
| M-4 | Os comprovativos conservam-se pelo prazo legal aplicável — o número de anos não é conhecido de quem respondeu. | retenção de comprovativos / operação | T5 |

**Autoridades nomeadas pela dona do pedido (além dela própria)**:
- responsável de contabilidade — factos do dia-a-dia do processo (T1–T6)
- responsável de sistemas — factos de orçamento/sistemas
- administração — orçamento e taxa por quilómetro
- director financeiro — limiar de aprovação (autoridade a consultar para o conflito 250 vs 500)
- compras — licenças da plataforma low-code

**Ficheiros nomeados na entrevista, ainda não entregues** (perguntado — passo 4d2 —, resposta: começa sem eles):
- folha de cálculo de reembolso (modelo em branco ou exemplo preenchido)
- ERP-X — acesso, exportação ou documentação da interface de pagamentos a colaboradores
- deliberação da administração que fixa a taxa por quilómetro (M-3)

**Regras**: isto é a hipótese do dono, não facto verificado — `/frame` confirma ou corrige cada `M-n` com evidência; nada aqui foi inferido pelo executor; nenhum nome de fornecedor ou produto entra nesta fase.
