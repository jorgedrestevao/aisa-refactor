## R-01 — operations

**What matters**

O processo real corre inteiro em folha de cálculo e email (`spreadsheet_and_mailbox_anchors`): o colaborador preenche uma folha e envia por email com fotografias dos recibos; a contabilidade copia os valores à mão para uma segunda folha e depois para o ERP-X; a aprovação (chefia directa ou director financeiro, por valor) acontece nalgum ponto desse percurso, sem que nenhuma fonte diga exactamente onde nem se bloqueia o passo seguinte (U-001, perspectiva de controlo — a mecânica de onde é que o gate está é operações; se esse gate é efectivo é controlo). O ERP-X existe e até tem uma interface para pagamentos a colaboradores, mas nunca foi usada para reembolsos — hoje não há **nenhum** sistema com interface programática para este processo (`system_without_programmatic_interface`). A dupla transcrição manual (folha → folha → ERP-X) é o candidato mais forte a complexidade acidental (A-001), mas fica hipótese até Options confirmar.

**Tensions / risks**

O volume citado (~300 pedidos/mês) é dito de memória, sem registo mostrado (A-002) — suficiente para planear, não para dimensionar com precisão. Não há hoje um identificador estável que ligue as três representações do mesmo pedido (folha → folha → ERP-X) — U-004 marca isto como um requisito provável de qualquer solução, não uma falha actual. Não se sabe se o "demora semanas" relatado no pedido vem da espera pela aprovação, da transcrição manual ou de emails perdidos (U-005) — sem isto, não se sabe onde a solução tem de intervir primeiro.

**Open evidence**

- ADOPT `chain: reembolso completo` → C-003 (cadeia ponta-a-ponta confirmada pela entrevista)
- MAP `task: preenchimento manual` → C-003 (already covers the manual fill-in step)
- MAP `task: dupla transcrição manual` → C-003 (already covers the double manual copy)
- ADOPT `constraint: ERP-X existente` → C-004
- ADOPT `exception: duplicados` → C-005
- ADOPT `exception: recibo ilegível` → C-006
- ADOPT `exception: email perdido` → C-007
- ADOPT (Genuine vs accidental complexity, não rotulada) → A-001
- ADOPT (End-to-end flow — frequência, não rotulada) → A-002
- ADOPT (derivado de `entrevista-financas.md ¶1`, cue `stable_business_key_availability`) → U-004
- ADOPT (cues `step_duration` / `long_running_wait_and_approval_shape`) → U-005
