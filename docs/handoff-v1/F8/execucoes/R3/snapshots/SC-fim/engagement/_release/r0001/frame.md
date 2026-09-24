# Frame — f8-r3-fx02 / Round F-01

## Single problem sentence

**O problema é a falta de um sistema único para pedir, aprovar e encomendar equipamento informático — hoje tudo corre por email e por uma folha de cálculo, sem preço sempre actualizado e, segundo o responsável de compras, sem confirmação de recepção que evite reenvios (assumido, ainda por confirmar com o requerente) —, sentido por compras (retrabalho com encomendas a dobrar) e, na reconciliação, por divergências de arredondamento reportadas à contabilidade (ainda por confirmar se a contabilidade sente o mesmo impacto); custa hoje pedidos duplicados e divergências reais já ocorridas, ainda sem envelope quantificado (falta o volume, o tempo por passo e a taxa horária carregada); a evidência vem da entrevista ao responsável de compras e da nota sobre os dados do catálogo.**

## Anchors

| Clause | Source persona(s) | SU id(s) / input citation |
|---|---|---|
| O problema é (falta de sistema único; hoje email/folha de cálculo) | analista, revisor | C-002 |
| ...sem preço sempre actualizado | analista, revisor | C-004 |
| ...sem confirmação de recepção que evite reenvios (assumido) | revisor (correcção por evidência) | A-002 (Assumed — corrigida a formulação: a proposta original citava-a como facto; a evidência só sustenta assumido) |
| Felt by compras (retrabalho com encomendas a dobrar) | analista, revisor | R-001 |
| Divergências de arredondamento reportadas na reconciliação com a contabilidade | revisor (correcção por evidência) | A-001, `inputs/entrevista-processo.md ¶3` (enquadramento.md#T1 não declara a contabilidade como actor — por isso "sentir o mesmo impacto" fica por confirmar, não afirmado) |
| Costs today (duplicados, divergências reais; sem envelope quantificado) | analista | A-001, A-004, A-005 (quantificação bloqueada por U-001, U-009, U-010) |
| Evidence is (entrevista-processo.md, nota-dados.md) | analista, revisor | `_capture/entrevista-processo.md.text.md`, `_capture/nota-dados.md.text.md` |
| M-1 (chefia nunca aprova pedido próprio) | analista, revisor | M-1 — confirmado, sem correcção |
| M-2 (acima do limiar vai à direcção financeira; limiar = 5 000 €) | analista, revisor | M-2, C-006 — confirmado, sem correcção |
| M-3 (auditoria vê quem aprovou o quê e quando) | analista, revisor | M-3 — confirmado, sem correcção; mecanismo ainda por desenhar (U-006) |
| M-4 (documentos conservados 10 anos) | analista, revisor | M-4 — confirmado, sem correcção |

**Correcções por evidência aplicadas nesta síntese** (revisor, `F-01-reviewer.md`): duas cláusulas da proposta original do analista excediam o que a evidência sustenta — "sem confirmação de recepção" estava ancorada a A-002 (Assumed), não citada, e apresentada como facto; "sentido... pela contabilidade" afirmava um impacto sentido por um actor que `enquadramento.md#T1` não declara. Ambas corrigidas por reformulação (nunca por escolha entre duas afirmações concorrentes — nenhuma das duas tinha uma alternativa com locator próprio, por isso não geram linha `Conflicted`, geram apenas a frase corrigida ao nível da evidência).

## Open questions still material to Framing

- U-001 — com que frequência ocorre o processo (pedidos por dia/semana/mês)?
- U-002 — em que contexto os colaboradores fazem hoje o pedido?
- U-004 — ler preços em tempo real do ERP-X ou manter cópia própria?
- U-006 — que mecanismo regista quem aprovou o quê e quando, de forma fiável?
- U-007 — qual é o envelope orçamental, o modelo de financiamento e o limiar de aprovação do projecto?
- U-008 — como se sabe que o processo, e o projecto que o digitaliza, correu bem?
- U-009 — quanto tempo demora hoje cada passo do processo?
- U-010 — qual é a taxa horária carregada de quem hoje faz cada passo?

## Conflicts surfaced (and how recorded)

- X-001 — o caminho de urgência salta a aprovação prévia da chefia; não está declarado se também salta a aprovação da direcção financeira acima do limiar — `partes: operations∧governance`, `criticidade: Critical`. Sem resposta do dono (declarou não ter essa informação) e sem evidência interna do engagement que resolva o conflito em qualquer direcção, confirmado após duas passagens de Discovery e revisão independente (`council-log.md`, R-01/R-02). A fase avançou por `/frame --override` (razão registada em `decisions.md`); X-001 mantém-se Conflicted e visível — fecha antes de qualquer entrega final que dependa dele.

## What must survive into Options

### Process meaning
- C-002 — hoje, o colaborador pede por email; a chefia aprova/rejeita; compras regista e encomenda.
- C-005 — o valor do pedido é quantidade × preço unitário por linha, somado, mais IVA.

### Business invariants
- M-1 — a chefia nunca aprova um pedido feito por si própria.
- M-2 — acima do limiar (5 000 €, C-006), o pedido tem de ir à direcção financeira.
- M-3 — a auditoria interna tem de saber quem aprovou o quê e quando.
- M-4 — os documentos de compra são conservados 10 anos.

### Structural constraints
- C-004 — a verdade dos preços vive hoje no ERP-X (condição confirmada que gate a arquitectura de dados de qualquer opção).
- U-004 — ler em tempo real do ERP-X ou manter cópia própria — ainda em aberto, `swing: dimensionante` (muda o modelo de dados e o plano de integração, não elimina classes inteiras de solução).

### Decision-changing Unknowns
- (none) — nenhuma `Unknown` aberta na Shared Understanding carrega `swing: decisivo`; as mais estruturais (U-004, U-006) são `dimensionante` — mudam desenho e esforço, não a classe de solução viável.

### Material scope / task obligations
- C-008 — o âmbito autorizado cobre o pedido, a aprovação e a passagem a compras; gestão de stock e recepção física ficam fora (declarado pelo dono, `pedido.md · ¶4`).
- U-006 — mecanismo de registo de quem aprovou o quê e quando ainda por desenhar (obrigação de M-3).
