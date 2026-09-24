## R-01 — data

**What matters**

Antes de chegar ao ERP-X, o pedido de reembolso existe em três representações copiadas à mão — a folha do colaborador, uma segunda folha da contabilidade, e só depois o ERP-X — sem que nenhuma fonte descreva um sistema de registo único ou uma chave que ligue as três (A-003). O ERP-X é o único sistema com alguma pretensão de ser "registo", mas a sua interface de pagamentos nunca foi usada para este processo (ver perspectiva de operações, C-004).

**Tensions / risks**

Os recibos anexados por email são fotografias — anexos binários cujo conteúdo (dados pessoais para além do valor) e tratamento actual não foram inspeccionados (U-010). Sem chave estável entre as três representações (perspectiva de operações, U-004), qualquer solução tem de decidir onde nasce o identificador do pedido — decisão de modelo de dados, não facto a assumir.

**Open evidence**

- ADOPT `chain: reembolso completo` (ângulo de linhagem/fonte-de-verdade, distinto da leitura de operações) → A-003
- ADOPT (cue `attachment_and_binary_volume` / `sensitivity_classification`, não rotulada) → U-010
- DISMISS `constraint: licenciamento por confirmar` — pertence à viabilidade financeira do licenciamento (perspectiva financeira, U-008), não a um facto de dados
