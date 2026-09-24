# Enquadramento — f8-r3-fx02

> Dono do processo: Director de Sistemas de Informação, Organização Exemplo
> Data: 2026-09-24
> Executor: aisa (piloto F8, execução R3)
> Pedido literal: «Queremos digitalizar os pedidos de equipamento informático (portáteis, monitores, acessórios). A plataforma é Power Platform: foi a decisão corporativa da direcção de SI (deliberação interna DSI-SINT-07, sintética) e não está em discussão.»

## T1 · actors

O requerente, que cria e consulta os seus pedidos; a chefia, que aprova ou rejeita os pedidos da sua equipa; compras, que vê os pedidos aprovados e regista a encomenda; a direcção financeira, que aprova os pedidos acima do limiar do despacho; e a auditoria interna, que quer saber quem aprovou o quê e quando. Quem manda formalmente no processo: não sei dizer, não está escrito.

## T2 · trigger

Começa quando um colaborador pede equipamento por email. Com que frequência: não sei.

## T3 · activities

O colaborador pede por email; a chefia responde «aprovado»; compras regista numa folha de cálculo e encomenda. Acima de um certo valor tem de ir à direcção financeira. Os pedidos urgentes, quando há uma avaria que impede trabalhar, vão directamente a compras e a chefia valida depois, no mesmo dia.

## T4 · outcomes

Sai a encomenda, registada por compras. Como se sabe que correu bem: não sei dizer.

## T5 · invariants

- M-1: A chefia nunca aprova um pedido feito por si própria.
- M-2: Acima do limiar definido em despacho, o pedido tem de ir à direcção financeira.
- M-3: A auditoria interna tem de saber quem aprovou o quê e quando.
- M-4: Os documentos de compra são conservados 10 anos.

## T6 · failure_today

Às vezes a mesma pessoa manda o mesmo pedido duas vezes porque acha que o email não chegou, e encomendamos a dobrar. Já houve diferenças de um cêntimo com a contabilidade por causa do arredondamento. A cópia do catálogo na folha de compras é actualizada à mão, quando alguém se lembra. Quanto custa: não sei.

## T7 · change_requested

Digitalizar o pedido, a aprovação e a passagem a compras. Fica de fora a gestão de stock e a recepção física.

## Invariantes

| id | invariante | o que orienta | fonte |
|----|-----------|----------------|-------|
| M-1 | A chefia nunca aprova um pedido feito por si própria. | quem pode aprovar o pedido — separação entre requerente e aprovador | Ninguém — só o dono |
| M-2 | Acima do limiar definido em despacho, o pedido tem de ir à direcção financeira. | quando o pedido sobe à direcção financeira | direcção financeira |
| M-3 | A auditoria interna tem de saber quem aprovou o quê e quando. | o registo de aprovações (quem aprovou o quê e quando) | auditoria interna |
| M-4 | Os documentos de compra são conservados 10 anos. | o prazo de conservação dos documentos de compra | Ninguém — só o dono |

**Autoridades adicionais declaradas pelo dono** (além de si): director de sistemas de informação — para a plataforma; direcção financeira — para o limiar do despacho; auditoria interna — para o registo de quem aprova.

**Regras**: hipótese do dono; `/frame` confirma ou corrige cada `M-n`; nada inferido; sem vendor/produto.

**Artefacto nomeado, não entregue**: o "despacho" que define o limiar de aprovação da direcção financeira — dono respondeu "ainda não tenho, começa sem ele" (passo 4d2).

**Pricing**: gate respondido `Não` — sem secção `## pricing`.

**Funding gate**: não declarado (dono: "não sei; isso não foi falado") — `context.json` sem a chave `funding_gate`; lentes tratam como `true`.
