# Process Model — f8-r5-fx01

> Sources: pedido.md (740e9e0c), entrevista-financas.md (b9e311ac), politica-rh.md (58b8ff72), nota-ti.md (ae4ab795)  |  Generated: 2026-09-24T16:40:00Z  |  Capture run: 1
> Source dispositions: pedido.md USED · entrevista-financas.md USED · politica-rh.md USED · nota-ti.md USED

## 1. File map

- `pedido.md` — o pedido síntetico da directora administrativa (quem pediu, o quê, âmbito). Todo o ficheiro é material (`USED`): 4 parágrafos, sem secções a descartar.
- `entrevista-financas.md` — notas de entrevista com o responsável de contabilidade: descreve o fluxo actual, o volume, o limiar de aprovação (versão oral), o esforço da contabilidade, os problemas do dia-a-dia e uma preferência pessoal por uma ferramenta pronta. Todo o ficheiro é material (`USED`): 6 parágrafos.
- `politica-rh.md` — excerto da política interna de deslocações (versão 3): quatro regras escritas (limiar de aprovação, recibo obrigatório, taxa por km, retenção de comprovativos). Todo o ficheiro é material (`USED`): 4 parágrafos.
- `nota-ti.md` — nota do responsável de sistemas: o ERP-X e o seu alcance actual, uma suspeita de licenciamento low-code por confirmar, a ausência de orçamento aprovado, e três alternativas ouvidas informalmente na casa. Todo o ficheiro é material (`USED`): 4 parágrafos.

Nenhuma fonte estruturada (`.xlsx`/`.xlsm`) nesta captura.

## 2. Column classification

Sem fonte estruturada nesta captura — não há colunas a classificar.

## 3. Business rules (PM-NNN)

Sem fonte estruturada nesta captura — nenhuma regra `PM-NNN` extraída de fórmula, validação ou formatação condicional. As regras de negócio detectadas nas fontes de texto entram na síntese (§4) e já estão registadas como invariantes do dono em `enquadramento.md` (M-1..M-4) e na Shared Understanding (Confirmed); não são duplicadas aqui.

## 4. Process synopsis (cross-source)

**Purpose**

`OBSERVED` O processo existe para processar o reembolso de despesas de deslocação de colaboradores — submissão, aprovação e pagamento. (`pedido.md · §Pedido (sintético) ¶4`)

**End-to-end flow**

`OBSERVED` Começa quando o colaborador preenche uma folha de cálculo por deslocação e a envia por email com fotografias dos recibos. (`entrevista-financas.md · §Notas de entrevista — responsável de contabilidade (sintético) ¶1`)
`OBSERVED` A contabilidade copia os valores da folha do colaborador para outra folha, e depois para o ERP-X. (`entrevista-financas.md ¶1`)
`OBSERVED` A aprovação acontece nalgum ponto desse percurso, condicionada pelo valor do pedido — a chefia directa abaixo do limiar, a direcção financeira acima. (`entrevista-financas.md ¶3`; `enquadramento.md#T3`)
`UNKNOWN` `chain: ponto de aprovação` Em que ponto exacto do percurso a aprovação é registada — antes ou depois da cópia para o ERP-X — e se bloqueia o passo seguinte antes de ser dada: nenhuma fonte descreve o mecanismo. (o que resolveria: PM-U-004)
`OBSERVED` Frequência: cerca de 300 pedidos por mês, valor dito de memória pela contabilidade, sem registo mostrado. (`entrevista-financas.md ¶2`)

**Actors**

`OBSERVED` O colaborador que se desloca preenche e envia o pedido. (`enquadramento.md#T1`)
`OBSERVED` A chefia directa aprova pedidos abaixo do limiar. (`enquadramento.md#T1`; `entrevista-financas.md ¶3`)
`OBSERVED` A direcção financeira/o director financeiro aprova pedidos acima do limiar. (`enquadramento.md#T1`; `entrevista-financas.md ¶3`; `politica-rh.md ¶1`)
`OBSERVED` A contabilidade processa e paga, e faz as duas cópias manuais (folha → folha → ERP-X). (`enquadramento.md#T1`; `entrevista-financas.md ¶1`)
`UNKNOWN` `actor: autoridade formal por saber` Quem manda formalmente no processo — o próprio dono declara não saber dizer. (`enquadramento.md#T1`; PM-U-005)

**Inputs**

`OBSERVED` A folha de cálculo por deslocação preenchida manualmente pelo colaborador, com fotografias dos recibos anexadas por email — manual, por pedido. (`entrevista-financas.md ¶1`)
`UNKNOWN` A "outra folha" para onde a contabilidade copia os valores antes do ERP-X — ficheiro não entregue nesta captura. (RESPOSTA F8 ao pedido de artefacto nomeado, piloto)
`UNKNOWN` A taxa por quilómetro em vigor — fixada em deliberação da administração não entregue nesta captura. (`enquadramento.md#M-3`; `politica-rh.md ¶3`; PM-U-002)

**Transformation / calculation stages**

`OBSERVED` `chain: reembolso completo` colaborador preenche folha → envia por email com recibos → contabilidade copia valores para segunda folha → contabilidade copia para ERP-X → aprovação (chefia directa ou director financeiro, por valor) → pagamento ao colaborador. (`entrevista-financas.md ¶1, ¶3`; `enquadramento.md#T3, #T4`)
`HYPOTHESIS` `chain: ordem aprovação vs ERP-X` A ordem exacta entre "aprovação" e "registo no ERP-X" não está fixada pelas fontes — pode ser em qualquer sentido. (o que resolveria: PM-U-004)

**Intermediate state**

`OBSERVED` Existe um estado intermédio: uma segunda folha interna da contabilidade, entre a folha do colaborador e o ERP-X. (`entrevista-financas.md ¶1`)

**Decisions**

`OBSERVED` Decisão de aprovar/rejeitar um pedido, por valor: chefia directa abaixo do limiar, direcção financeira acima. (`entrevista-financas.md ¶3`; `politica-rh.md ¶1`)
`OBSERVED` (conflito) `conflict: limiar de aprovação` O valor do limiar diverge entre fontes: a entrevista e a declaração do dono dizem 500€ (`entrevista-financas.md ¶3`), a política escrita diz 250€ (`politica-rh.md ¶1`). O próprio dono já sinalizou não saber qual vale (`enquadramento.md#M-2`). Isto é uma linha Conflicted candidata para a SU, não uma escolha desta captura.

**Outputs and consumers**

`OBSERVED` `Outputs pagamento` Output = pagamento ao colaborador; consumidor = o colaborador. (`enquadramento.md#T4`)
`UNKNOWN` `outputs: critério de sucesso do pagamento` Critério de sucesso do pagamento — o dono não sabe dizer como se confirma que "correu bem". (`enquadramento.md#T4`)

**Exceptions and workarounds**

`OBSERVED` `exception: duplicados` Pedidos em duplicado quando o colaborador reenvia o email. (`entrevista-financas.md ¶5`)
`OBSERVED` `exception: recibo ilegível` Recibo ilegível bloqueia o reembolso — recibo obrigatório é invariante. (`politica-rh.md ¶2`; `enquadramento.md#M-1`)
`OBSERVED` `exception: email perdido` Pagamentos atrasados quando o email se perde. (`entrevista-financas.md ¶5`)

**Business invariants**

`OBSERVED` `invariant: recibo obrigatório` Sem recibo digitalizado legível não há reembolso. (`enquadramento.md#M-1`; `politica-rh.md ¶2`)
`OBSERVED` `invariant: limiar por valor (conflituoso)` Existe um limiar de valor que determina quem aprova; o número diverge entre fontes (500€ vs 250€) — ver conflito acima. (`enquadramento.md#M-2`; `entrevista-financas.md ¶3`; `politica-rh.md ¶1`)
`UNKNOWN` `invariant: taxa-km` A taxa por quilómetro é fixada por deliberação da administração; não disponível nesta captura. (`enquadramento.md#M-3`; `politica-rh.md ¶3`)
`UNKNOWN` `invariant: retenção` Os comprovativos são conservados pelo prazo legal aplicável; o número de anos não está declarado. (`enquadramento.md#M-4`; `politica-rh.md ¶4`)

**Structural constraints**

`OBSERVED` `constraint: ERP-X existente` Existe um sistema ERP-X com uma interface para registar pagamentos a colaboradores, nunca usada para reembolsos. (`nota-ti.md ¶1`)
`HYPOTHESIS` `constraint: licenciamento por confirmar` Pode já existir licenciamento de uma plataforma low-code no contrato corporativo — TI acredita que sim, mas não confirma; compras teria de confirmar. Entidade e mecanismo tratados de forma neutra — nenhum fornecedor ou produto nomeado (facto sobre um contrato já existente, não uma solução proposta). (`nota-ti.md ¶2`; PM-U-007)
`OBSERVED` `constraint: sem orçamento aprovado` Não existe orçamento aprovado para este projecto; qualquer custo recorrente precisa de aprovação da administração. (`nota-ti.md ¶3`; `context.json.funding_gate`)

**Material user tasks**

`OBSERVED` `task: preenchimento manual` O colaborador preenche manualmente uma folha de cálculo por deslocação e anexa fotografias de recibos por email. (`entrevista-financas.md ¶1`)
`OBSERVED` `task: dupla transcrição manual` A contabilidade transcreve manualmente os valores da folha do colaborador para uma segunda folha, e depois para o ERP-X — duas cópias manuais antes do sistema final. (`entrevista-financas.md ¶1`)

**Genuine vs accidental complexity**

`HYPOTHESIS` A dupla cópia manual (folha do colaborador → segunda folha → ERP-X) parece decorrer da falta de integração entre a folha e o ERP-X, não de uma necessidade de negócio — isto não está directamente evidenciado pelas fontes, fica hipótese a confirmar em Discovery. (`entrevista-financas.md ¶1`)

**Material unresolved semantics**

`UNKNOWN` `conflict: limiar de aprovação` Qual o limiar de aprovação que vale — 500€ ou 250€ — e qual a fonte autorizada para o corrigir. (`entrevista-financas.md ¶3` vs `politica-rh.md ¶1`; `enquadramento.md#M-2`)
`UNKNOWN` `actor: autoridade formal por saber` Quem manda formalmente no processo. (`enquadramento.md#T1`)
`UNKNOWN` `outputs: critério de sucesso do pagamento` Como se confirma que um pagamento "correu bem". (`enquadramento.md#T4`)
`UNKNOWN` `custo actual: horas e valor` Quantas horas por semana a contabilidade gasta neste processo, e qual o custo total actual. (`entrevista-financas.md ¶4`)
`OBSERVED` `sinal: preferência por ferramenta pronta` A responsável de contabilidade manifestou preferência pessoal por comprar uma ferramenta pronta, já vista numa feira — não é requisito nem invariante do dono do pedido (a directora administrativa); sinal a pesar pelas perspectivas de negócio/financeira antes das Options, para não estreitar alternativas prematuramente. (`entrevista-financas.md ¶6`)

## 4bis. Cadeia de cálculo (por saída)

calc-chain: absent (sem fonte estruturada nesta captura)

## 5. Anomalies & silent failures

Sem fonte estruturada nesta captura — não há replay nem anomalias de fórmula a reportar.

## 6. Interrogation list (PM-U-NNN)

| id | question | why it matters | suggested respondent (role) | criticidade | custo | swing | classe | tipo | impacto |
|---|---|---|---|---|---|---|---|---|---|
| PM-U-001 | Qual o limiar de aprovação correcto — 500€ (entrevista/dono) ou 250€ (política escrita)? | Determina quem aprova cada pedido e a rota de aprovação que qualquer solução tem de implementar; sem isto o desenho da regra de aprovação fica indeterminado. | `role: direcção financeira` \| `fonte: política interna de deslocações actualizada` | Critical | documento | dimensionante — muda a regra de aprovação (quem aprova cada pedido, por valor) que qualquer solução tem de codificar | processo | conflict | funcional, aceitacao: regra e critério de aceitação de "quem tinha de aprovar este pedido" |
| PM-U-002 | Qual a taxa por quilómetro em vigor (deliberação da administração)? | Necessária para calcular correctamente o reembolso em viatura própria; sem ela não se valida nem constrói a regra de cálculo. | `role: administração` \| `fonte: deliberação da administração sobre taxa por km` | Critical | documento | dimensionante — muda o valor usado na fórmula de cálculo do reembolso por km | processo | fact_gap | funcional: fórmula de cálculo do reembolso por quilómetro |
| PM-U-003 | Por quantos anos se conservam os comprovativos de despesa (prazo legal aplicável)? | Define o requisito de retenção/arquivo que a solução tem de implementar. | `role: direcção financeira / jurídico` \| `fonte: enquadramento legal aplicável à retenção de comprovativos` | Med | documento | dimensionante — muda o prazo de retenção/arquivo a implementar | processo | fact_gap | operacao: prazo de retenção/arquivo dos comprovativos |
| PM-U-004 | Em que ponto exacto do percurso a aprovação é registada — antes ou depois da cópia para o ERP-X — e bloqueia o passo seguinte? | Define se a solução tem de impedir o pagamento antes da aprovação ou apenas registá-la depois — afecta o desenho do controlo de fluxo. | `role: contabilidade` \| `fonte: observação directa do processo actual` | Critical | reuniao | dimensionante — muda o desenho do gate de aprovação no fluxo | processo | fact_gap | funcional: onde o controlo de aprovação bloqueia o passo seguinte |
| PM-U-005 | Quem manda formalmente no processo, além dos papéis de aprovação por valor? | Relevante para a governação do processo e para quem autoriza excepções não previstas nas regras de valor. | `role: administração` \| `fonte: organograma / regulamento interno` | Low | email | dimensionante — define papéis/permissões de governação no desenho futuro | processo | fact_gap | operacao: papéis e permissões de governação do processo |
| PM-U-006 | Quantas horas por semana a contabilidade gasta neste processo, e qual o custo total actual? | Necessário para quantificar o caso de negócio (poupança esperada) e o retorno de qualquer opção. | `role: contabilidade / direcção financeira` \| `fonte: medição de tempos (não existe registo hoje)` | High | spike | dimensionante — muda a quantificação do caso de negócio/poupança de qualquer opção | processo | fact_gap | viabilidade: quantificação do custo actual / caso de negócio |
| PM-U-007 | Existem já licenças de uma plataforma low-code no contrato corporativo? | Pode alterar o custo incremental de qualquer opção que dependa de licenciamento — entitlement já existente muda o cálculo de viabilidade. | `role: compras` \| `fonte: contrato corporativo de licenciamento` | Med | email | decisivo — pode tornar mais barata qualquer opção que dependa desse licenciamento, mudando qual sobrevive em Options | processo | fact_gap | viabilidade: custo incremental de licenciamento por opção |

## 7. Not captured

Nenhuma fonte estruturada nesta captura — não há VBA, folhas protegidas, fórmulas por ler nem intervalos nomeados. As 4 fontes de texto extraíram todas com estado `ok`; nenhuma falhou, foi saltada ou ficou vazia. Ficheiros nomeados na entrevista mas não entregues (a folha de cálculo do colaborador, a segunda folha da contabilidade, um export/documentação do ERP-X, a deliberação da administração sobre a taxa por km) ficam registados como `UNKNOWN`/`TO-READ` acima (PM-U-002, PM-U-004) e no pedido de artefacto nomeado deste piloto — nenhum foi entregue até esta captura.
