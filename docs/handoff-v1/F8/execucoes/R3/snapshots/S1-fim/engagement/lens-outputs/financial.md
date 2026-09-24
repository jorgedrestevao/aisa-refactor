## R-01 — financial

**What matters.** `context.json.funding_gate` não está declarado (dono: "não sei; não foi falado") — a chave fica ausente e, por omissão, trata-se como `true`: as quatro perguntas de financiamento (envelope, CAPEX/OPEX, modelo, limiares) ficam activas nesta engagement. **Correcção pós-revisão independente**: o envelope de custo as-is escreve-se, não se pergunta (`library/kernel/lens-checklists.md` → *Financial*, *Apply*) — mesmo sem números do cliente. Escrita agora a estrutura (A-005): custo = volume × tempo por passo × taxa horária carregada + custo dos duplicados + custo das divergências de arredondamento. Os três factores que faltam para quantificar ficam Unknown, não bloqueiam a escrita da fórmula: volume (U-001, operations), tempo por passo (U-009, operations) e taxa horária carregada (U-010, financial).

**Tensions / risks.** Sem os três factores (U-001, U-009, U-010), o envelope fica na forma, não no número — mas a forma já está escrita e visível (A-005), como o contrato exige. Sem envelope orçamental do projecto (U-007, distinto do envelope de custo as-is), o caso de negócio fica sem tecto de investimento conhecido.

**Open evidence.** (none — nenhuma linha de síntese do processo nem PM-U foi atribuída a esta perspectiva; A-005, U-007 e U-010 nascem de leitura directa do checklist financeiro, não de disposição de §4/§6.)
