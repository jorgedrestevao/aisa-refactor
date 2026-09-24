# As-Is — f8-r3-fx02

## End-to-end process today

1. O colaborador (requerente) pede equipamento por email (C-002).
2. A chefia aprova ou rejeita por email — nunca aprova o seu próprio pedido (M-1).
3. Compras regista o pedido numa folha de cálculo e faz a encomenda (C-002), usando uma cópia manual do catálogo de preços que vive de facto no ERP-X (C-004).
4. Acima do limiar de 5 000 €/pedido (C-006), o pedido tem de ir à direcção financeira (M-2) — o ponto exacto em que isso acontece no fluxo normal não está descrito para além do limiar em si.
5. Excepção: pedidos urgentes (avaria que impede trabalhar) vão directamente a compras; a chefia tem até ao fim do dia útil seguinte para validar — já não no mesmo dia — e, sem validação dentro desse prazo, compras suspende a encomenda até haver validação (A-006, was C-003, base: nota-urgentes.md, responsável de compras). Não está declarado se esta via também salta a validação da direcção financeira quando o valor ultrapassa o limiar — conflito aberto, X-001, sem resposta nesta nota.

## Volume and cycle time

Nem o volume (pedidos por dia/semana/mês, U-001) nem o tempo de ciclo por passo (U-009) foram medidos — ambos ficam Unknown, sem número inventado. A fórmula do custo as-is já está escrita (A-005: volume × tempo por passo × taxa horária carregada + custo dos duplicados + custo das divergências), mas os três factores continuam por preencher.

### Passos e tempo (P-5)

| passo | quem | tempo | estado · base | fonte |
|---|---|---|---|---|
| pedir por email | requerente | — | Unknown (U-009, custo=email) | entrevista-processo.md · ¶1 |
| aprovar/rejeitar por email | chefia | — | Unknown (U-009, custo=email) | entrevista-processo.md · ¶1 |
| registar em folha de cálculo | compras | — | Unknown (U-009, custo=email) | entrevista-processo.md · ¶1 |
| encomendar | compras | — | Unknown (U-009, custo=email) | entrevista-processo.md · ¶1 |
| via de urgência: encomendar antes, validar depois; se não validado, suspende | compras, chefia | fim do dia útil seguinte (validação); suspensão se ultrapassado | Assumed — A-006, was C-003 (o único tempo declarado nesta lente; base: resposta de terceiro, sem autoridade nomeada) | nota-urgentes.md ¶2, ¶3 |

Sem total de ciclo — nenhum dos quatro passos regulares tem duração medida; nada a somar sem inventar.

## Personas and their experience

Cinco populações usam o processo hoje, sem nenhuma tarefa estruturada de ecrã — tudo corre por email e folha de cálculo (lens-outputs/user.md (primeira passagem de Discovery)): requerente, chefia, compras, direcção financeira, auditoria interna (matriz-papeis.md). O contexto real de uso do requerente — secretária vs terreno, dispositivo, ligação — não foi declarado e fica em aberto (U-002); importa para o desenho da interacção e, nesta ronda, para a escolha entre O-001 e O-002 (decisions.md#D-002).

## Exceptions, handoffs, and tribal knowledge

O ponto único de conhecimento tribal identificado é o valor do despacho financeiro — ninguém sabia de cor antes da resposta do dono (resolvido → C-006). A via de urgência (A-006, was C-003) é a excepção documentada mais relevante, e é também a origem do único conflito ainda aberto no engagement (X-001): salta a aprovação da chefia por desenho, mas não está escrito se também salta o controlo financeiro — a mudança de prazo (nota-urgentes.md) não resolve esse conflito.

## Top friction points

- Pedidos duplicados por reenvio — o requerente julga que o email não chegou e reenvia, sem confirmação de recepção (R-003, causa em A-002).
- Cópia manual do catálogo de preços, sem cadência de actualização definida — risco de preços desactualizados na encomenda (R-004).
- Arredondamento indefinido até esta ronda — já causou divergências reais com a contabilidade antes de ser resolvido (C-007).
- Via de urgência sem regra clara face ao controlo financeiro (X-001) — ainda aberta.
- Ausência de rasto fiável de aprovações para a auditoria interna — email e folha de cálculo não garantem o registo que M-3 exige (U-006).
- Nenhum critério de sucesso declarado para o projecto (U-008).
