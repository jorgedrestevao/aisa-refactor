# Chairman Synthesis — Round F-01 / Phase Framing

## Personas heard
- analista integrado, frame-reviewer

## Overlaps → strengthened
- (none) — Framing corre com uma proposta (analista) e uma revisão (revisor), não duas propostas independentes; não há sobreposição de duas fontes a reforçar um facto novo.

## Gaps → carried as Assumed/Unknown
- "O âmbito autorizado cobre o pedido, a aprovação e a passagem a compras; gestão de stock e recepção física ficam fora" — proposta pelo analista, ancorada em `pedido.md · ¶4` (declaração datada do dono, persistida em `_capture/pedido.md.text.md`) → **C-008 (Confirmed)** — locator de classe *Confirmed threshold* (declaração do dono), não apenas concordância entre personas.

## Contradictions → Conflicted
- (none) novas nesta passagem. X-001 já existia (R-01/governance), transportado para `frame.md` → *Conflicts surfaced*, não reaberto nem resolvido aqui.

## Admissão de perguntas
- Nenhuma `Unknown` nova proposta pelo analista ou pelo revisor nesta passagem — todas as perguntas citadas (U-001, U-002, U-004, U-006, U-007, U-008, U-009, U-010) já existiam da Discovery; nenhuma admissão nova a registar.

## Correcções por evidência (achados do revisor, kind: fact)
- Achado 1 (cláusula "sem confirmação de recepção"): A-002 é `Assumed`, não citada na proposta original, apresentada como facto. Locator do revisor: `shared-understanding.md#A-002`, `entrevista-processo.md ¶6`. Correcção aplicada: frase reformulada para declarar o assumido explicitamente («segundo o responsável de compras... assumido, ainda por confirmar com o requerente»). Sem linha nova — A-002 já está correctamente `Assumed`.
- Achado 2 (cláusula "sentido... pela contabilidade"): `enquadramento.md#T1` não declara a contabilidade como actor; o impacto só está reportado do lado de compras (`entrevista-processo.md ¶3`). Correcção aplicada: frase reformulada para "divergências... reportadas na reconciliação com a contabilidade", sem afirmar que a contabilidade sente o impacto. Sem linha nova.
- Achado 3 (recomendação, formatação das âncoras): aplicado — tabela de âncoras em `frame.md` separa cada sub-cláusula com a sua própria referência.
- Nenhum dos dois achados factuais tinha uma alternativa concorrente com locator próprio — por isso corrigem a frase por evidência (downgrade ao nível que a evidência sustenta), nunca geram `Conflicted` (`partes: analista∧revisor` seria para uma contradição de facto entre as duas fontes, não para um exagero de certeza sobre uma única fonte).

## Risks captured
- R-001 — pedidos duplicados por reenvio, sem mecanismo de detecção hoje (já existente, R-01).
- R-002 — cópia do catálogo actualizada à mão, sem cadência definida (já existente, R-01).

## SU rows written this round
- C-008 — o âmbito autorizado cobre o pedido, a aprovação e a passagem a compras; gestão de stock e recepção física ficam fora.

## Phase artefact written
- `frame.md` — frase do problema (corrigida por evidência face à proposta do analista), âncoras, perguntas em aberto, X-001 transportado, bloco "o que tem de sobreviver".
