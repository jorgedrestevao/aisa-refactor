## frame-reviewer — Round F-01 / Phase Framing

### Coverage of the review
- Clause "o problema é X" (falta de sistema único; email/folha de cálculo; sem confirmação de recepção; preço nem sempre actualizado) — checked: `shared-understanding.md` C-002, A-003, C-004; `inputs/entrevista-processo.md` ¶1, ¶6; `inputs/nota-dados.md` ¶1; `_capture/entrevista-processo.md.text.md`, `_capture/nota-dados.md.text.md` (paragraph numbering verified against raw).
- Clause "felt by Y" (compras: retrabalho; contabilidade: arredondamento) — checked: `shared-understanding.md` A-001, R-001; `inputs/entrevista-processo.md` ¶3, ¶6; `enquadramento.md` T1 (actor list).
- Clause "costs Z today" (pedidos duplicados, divergências reais, sem envelope quantificado) — checked: `shared-understanding.md` A-001, A-004, A-005, U-001, U-009, U-010.
- Clause "evidence is W" (entrevista-processo.md, nota-dados.md) — checked: `_capture/evidence-index.md`; `_capture/entrevista-processo.md.text.md` ¶1/¶3/¶6; `_capture/nota-dados.md.text.md` ¶1; raw `inputs/` sources.
- M-1 (chefia nunca aprova pedido próprio) — checked: `enquadramento.md` T5/M-1; `shared-understanding.md` row M-1; `inputs/matriz-papeis.md` ¶2. Confirmed, no discrepancy.
- M-2 (acima do limiar vai à direcção financeira) — checked: `enquadramento.md` M-2; `shared-understanding.md` M-2, C-006; `inputs/matriz-papeis.md` ¶4. Confirmed, threshold value (5000€) traced correctly to C-006.
- M-3 (auditoria vê quem aprovou o quê e quando) — checked: `enquadramento.md` M-3; `shared-understanding.md` M-3, U-006; `inputs/matriz-papeis.md` ¶5. Confirmed, mechanism correctly left open via U-006.
- M-4 (documentos conservados 10 anos) — checked: `enquadramento.md` M-4; `shared-understanding.md` M-4; `inputs/nota-dados.md` ¶3. Confirmed, no discrepancy.
- Survival-block candidates (C-002, C-005, C-004, U-004, M-1..M-4) — checked against `shared-understanding.md` rows cited; all traced correctly, no fabricated ids.
- "Perguntas que mudam o caminho (decisivas): (none)" — checked: `shared-understanding.md` Unknown table, `swing` column for all U-001..U-010 — none carries `decisivo`, all `dimensionante`. Claim holds.
- X-001 (urgent path vs financial threshold, Critical, Conflicted) omitted from headline — checked: `shared-understanding.md` X-001; `council-log.md` R-02 entries. Surfaced adequately in proposal's own "Conflicts seen" section with correct override trail; not folded into headline — acceptable, not flagged as a finding.

### Findings

- **Target**: headline clause "sem confirmação de recepção"
  **Severity**: material
  **Kind**: fact
  **Premise/evidence**: `shared-understanding.md` → A-002 is the only row that could support this claim, and it is `Assumed` ("inferência razoável a partir de 'acha que o email não chegou' — entrevista-processo.md · ¶6"), not Confirmed. The raw source (`inputs/entrevista-processo.md` ¶6 / [C6]) reports duplicate sends caused by doubt, not a stated absence of a receipt-confirmation mechanism. A-002 is not cited anywhere in the proposal's evidence anchors.
  **Failure scenario**: Options/blueprint treats "no receipt confirmation exists" as an established current-state fact rather than a working assumption; a feature gets built on it without checking whether some ad-hoc acknowledgment already exists, risking a mis-scoped fix or missing the real cause of duplicates.
  **Closing condition**: cite A-002 explicitly (flagged Assumed) in the evidence anchors, or reword the clause to state it as an assumption, or get owner/responsável-de-compras confirmation that no acknowledgment mechanism exists today.

- **Target**: headline clause "felt by ... pela contabilidade (divergências de arredondamento)"
  **Severity**: material
  **Kind**: fact
  **Premise/evidence**: `enquadramento.md` T1 declares the process actors (requerente, chefia, compras, direcção financeira, auditoria interna) — contabilidade is absent. The two rows the proposal cites for "felt by" (`shared-understanding.md` A-001, R-001) attribute impact/rework to compras only, not to contabilidade. Raw source `inputs/entrevista-processo.md` ¶3 [C3] reports a reconciliation discrepancy from compras' point of view ("já houve diferenças de um cêntimo com a contabilidade"), not a stated pain point voiced by contabilidade itself.
  **Failure scenario**: contabilidade gets counted as a confirmed stakeholder of the problem without ever being interviewed or declared by the owner; downstream phases may assume a sign-off or feature contabilidade needs, or skip validating with contabilidade because the frame already asserts the pain is known.
  **Closing condition**: owner adds contabilidade to the declared actor list, or an interview/citation captures contabilidade's own account of the impact; otherwise reword the clause to describe the discrepancy as observed in reconciliation ("divergências de arredondamento reportadas na reconciliação com a contabilidade") without asserting contabilidade "feels" the problem — or open an Unknown on whether contabilidade is a process actor.

- **Target**: evidence-anchors formatting for the "O problema é" clause
  **Severity**: minor
  **Kind**: recommendation
  **Premise/evidence**: no locator — the anchor bullet "O problema é ... — source: C-002, A-003" bundles three sub-claims (no single system; no receipt confirmation; catalog not always current) under a citation set that only covers the first; the other two are only implicitly reachable via the separate generic "Evidence is" bullet.
  **Failure scenario**: a later reader auditing the sentence can't tell at a glance which row backs which sub-claim, and may assume C-002/A-003 cover all three when they cover only the first — masking finding 1 and 2 above.
  **Closing condition**: split the anchor bullet per sub-clause (e.g., "sem confirmação de recepção" → A-002 [Assumed]; "preço nem sempre actualizado" → C-004 / nota-dados.md ¶1).

### Alternative sentence (optional)
- O problema é a falta de um sistema único para pedir, aprovar e encomendar equipamento informático — hoje tudo corre por email e por uma folha de cálculo, sem preço sempre actualizado (C-004) e, segundo o responsável de compras, sem confirmação de recepção que evite reenvios (A-002, ainda por confirmar com o requerente) —, sentido por compras (retrabalho com encomendas a dobrar, R-001); há também divergências de arredondamento reportadas na reconciliação com a contabilidade, ainda por confirmar se a contabilidade sente o mesmo impacto; custa hoje pedidos duplicados e divergências reais já ocorridas, ainda sem envelope quantificado (falta o volume, o tempo por passo e a taxa horária carregada); a evidência vem da entrevista ao responsável de compras e da nota sobre os dados do catálogo.
