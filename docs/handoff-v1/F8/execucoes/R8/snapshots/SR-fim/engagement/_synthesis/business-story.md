# Business Story — f8-r3-fx02

## Why this engagement exists

O pedido chegou tal como está escrito: "Queremos digitalizar os pedidos de equipamento informático (portáteis, monitores, acessórios)" (context.json#literal_request), do director de sistemas de informação, que já tinha decidido a plataforma por deliberação interna (DSI-SINT-07). A frase que resume o problema (D-001): falta um sistema único para pedir, aprovar e encomendar equipamento — hoje tudo corre por email e por uma folha de cálculo (C-002), sem preço sempre actualizado (C-004) e, segundo o responsável de compras, sem confirmação de recepção que evite reenvios (assumido, A-002).

## Who actually feels the problem

Quem pede (director de SI) não é quem sente a dor. A dor concreta é sentida por compras — retrabalho com encomendas a dobrar (R-001, agora corrigido para R-003 por evidência de mecanismo) — e, na reconciliação, por divergências de arredondamento reportadas à contabilidade (A-001; ainda por confirmar se a contabilidade sente o mesmo impacto, per frame.md#Anchors). Cinco populações distintas usam o processo: requerente, chefia, compras, direcção financeira, auditoria interna (lens-outputs/user.md (primeira passagem de Discovery)), cada uma com tarefa e regra próprias (M-1, M-2, M-3).

## The impact in business terms

O impacto é qualitativo, não quantificado: sem número de frequência, tempo ou custo (A-001). A urgência não está declarada por data, só pelo custo observado — encomendas a dobrar, diferenças de cêntimos (lens-outputs/business.md (primeira passagem de Discovery)). O caso de negócio fica, por isso, dependente do que as lentes operations e financial ainda não apuraram: frequência (U-001), envelope orçamental do projecto (U-007), tempo por passo (U-009) e taxa horária carregada (U-010) — os três últimos alimentam a fórmula do custo as-is já escrita (A-005), sem os valores ainda por dentro.

## What success looks like to the sponsor

Ainda não está definido. O director de SI respondeu "não sei dizer" quando confrontado com a pergunta central de sucesso (enquadramento.md#T4) — sem critério explícito, a aprovação final do desenho corre o risco de ser julgada por padrões implícitos e divergentes entre o dono e os utilizadores (lens-outputs/business.md (primeira passagem de Discovery)). Esta lacuna foi admitida como pergunta aberta (U-008), a fechar pelo dono em `/decide` ou `/blueprint` — a decisão desta ronda (D-002) ainda não a fechou.

## Open issues still material to the business story

- U-008 — critério de sucesso do projecto, ainda por decidir.
- U-007 — envelope orçamental, modelo de financiamento e limiar de aprovação do projecto.
- U-001, U-009, U-010 — os três factores que fecham o envelope de custo as-is (A-005).
- X-001 — conflito ainda por resolver sobre o caminho de urgência vs limiar financeiro, aceite em aberto na decisão (D-002), a fechar antes de qualquer entrega final que dele dependa.
