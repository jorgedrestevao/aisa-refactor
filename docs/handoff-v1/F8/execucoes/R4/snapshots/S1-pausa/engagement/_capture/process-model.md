<!-- aisa.capture.process-model | authored inline (aisa-capture step 5), run 1 -->
# Process Model — f8-r4-fx01

> Sources: pedido.md (740e9e0c) · entrevista-financas.md (b9e311ac) · nota-ti.md (ae4ab795) · politica-rh.md (58b8ff72) | Generated: 2026-09-24 | Capture run: 1
> Source dispositions: pedido.md USED · entrevista-financas.md USED · nota-ti.md USED · politica-rh.md USED
> Sem fonte estruturada (`.xlsx`/`.xlsm`) nesta captura — as quatro fontes são texto (capture-lite/LT). §2, §3 e §4bis não se aplicam por essa razão, não por omissão.

## 1. File map

- `pedido.md` — o pedido do dono do processo (directora administrativa): motivação, tipo de decisão pedida (melhorar / comprar / construir), âmbito declarado. USED, inteira (4 parágrafos).
- `entrevista-financas.md` — entrevista à responsável de contabilidade: fluxo actual passo a passo, volume mensal, limiar de aprovação (versão oral), esforço, problemas do dia-a-dia, preferência pessoal por ferramenta pronta. USED, inteira (6 parágrafos).
- `nota-ti.md` — nota do responsável de sistemas: sistema actual (ERP-X) e o que a sua interface já faz, licenciamento low-code por confirmar, ausência de orçamento aprovado, alternativas já ouvidas na organização. USED, inteira (4 parágrafos).
- `politica-rh.md` — excerto da política interna de deslocações, versão 3: regras escritas (limiar de aprovação, recibo obrigatório, taxa por quilómetro, retenção de comprovativos). USED, inteira (4 parágrafos).

## 2. Column classification

Não aplicável — nenhuma fonte estruturada (`.xlsx`/`.xlsm`) neste `inputs/`.

## 3. Business rules (PM-NNN)

Não aplicável — regras `PM-NNN` provam-se por fórmula, validação ou formatação condicional de uma fonte estruturada, que não existe nesta captura. As regras de negócio conhecidas vêm de declaração do dono (`enquadramento.md#M-1..M-4`, ronda R-00) e da política escrita citada em §4 abaixo — não duplicadas aqui.

## 4. Process synopsis (cross-source)

**Purpose**

- OBSERVED — o processo decide e executa o reembolso de despesas de deslocação de colaboradores: submissão, aprovação e pagamento (`pedido.md · §Pedido (sintético) ¶4`). `Outputs reembolso`

**End-to-end flow**

- OBSERVED — o colaborador desloca-se, preenche uma folha de cálculo de despesas por deslocação e envia-a por email com fotografias dos recibos (`entrevista-financas.md · §Notas de entrevista — responsável de contabilidade (sintético) ¶1`).
- OBSERVED — a contabilidade copia os valores da folha do colaborador para outra folha, e depois lança-os no ERP-X (`entrevista-financas.md · §Notas de entrevista — responsável de contabilidade (sintético) ¶1`). `chain: email → folha intermédia → ERP-X → pagamento`
- OBSERVED — a aprovação acontece "algures" neste percurso, consoante o valor do pedido — não localizada a um passo fixo por nenhuma fonte (`entrevista-financas.md ¶1`, ¶3; confirmado na leitura de volta, `enquadramento.md#T3`).
- HYPOTHESIS — se a aprovação acontece antes ou depois da cópia para o ERP-X não está definido por nenhuma fonte. `chain: posição da aprovação no fluxo, por confirmar`

**Actors**

- OBSERVED — colaborador que se desloca (submete); chefia directa (aprova abaixo do limiar); direcção financeira (aprova acima do limiar); contabilidade (processa e paga) (`entrevista-financas.md ¶3`; leitura de volta `enquadramento.md#T1`).
- UNKNOWN — quem manda formalmente no processo (dono operacional) não está declarado — "não está escrito, não se sabe dizer" (`enquadramento.md#T1`). `processo: dono formal não identificado`

**Inputs**

- OBSERVED — folha de cálculo de despesas, preenchida manualmente pelo colaborador, por deslocação (`entrevista-financas.md ¶1`) — manual.
- OBSERVED — fotografias dos recibos, anexadas ao email (`entrevista-financas.md ¶1`) — manual.
- INFERRED — cerca de 300 pedidos por mês — valor dito de memória pela responsável de contabilidade, sem registo mostrado (`entrevista-financas.md ¶2`); base: relato não verificado, nenhum sistema consultado.

**Transformation / calculation stages**

- OBSERVED — folha do colaborador (email) → cópia manual para "outra folha" da contabilidade → lançamento no ERP-X → pagamento ao colaborador (`entrevista-financas.md ¶1`). Duas transcrições manuais antes do sistema de registo, sem fórmula nem validação automática a documentar entre passos.

**Intermediate state**

- OBSERVED — a "outra folha" da contabilidade é um estado intermédio entre o email do colaborador e o ERP-X; a sua estrutura, dono e retenção não são conhecidos de nenhuma fonte (`entrevista-financas.md ¶1`). `dados: folha intermédia da contabilidade, sem descrição`

**Decisions**

- OBSERVED — decisão de aprovar, por chefia directa ou por direcção financeira, consoante o valor do pedido (`entrevista-financas.md ¶3`; `politica-rh.md · §Excerto da política interna de deslocações, versão 3 (sintético) ¶1`).
- OBSERVED (entrevista) vs OBSERVED (política) — o valor do limiar diverge entre fontes: a entrevista diz 500€ (`entrevista-financas.md ¶3`), a política escrita diz 250€ (`politica-rh.md ¶1`); o próprio dono, na leitura de volta, confirmou não saber qual vale (`enquadramento.md#M-2`). A lente de `/round` regista a linha `Conflicted` — não decidida aqui. `chain: limiar de aprovação, valor em disputa`

**Outputs and consumers**

- OBSERVED — output = pagamento ao colaborador; consumidor = o próprio colaborador (`pedido.md ¶4`; `entrevista-financas.md ¶1`). `Outputs reembolso`
- UNKNOWN — critério de sucesso do processo ("como se sabe que correu bem") não está definido por nenhuma fonte (`enquadramento.md#T4`). `Outputs sem critério de sucesso declarado`

**Variants**

- Nenhuma variante por produto, canal ou tipo de colaborador identificada nas fontes — processo único para quem se desloca.

**Exceptions and workarounds**

- OBSERVED — o reenvio do email pelo colaborador produz pedidos em duplicado (`entrevista-financas.md ¶5`). `chain: reenvio de email → duplicado`
- OBSERVED — recibos ilegíveis impedem o reembolso (a política exige recibo digitalizado legível) e geram atrito (`entrevista-financas.md ¶5`; `politica-rh.md ¶2`).
- OBSERVED — pagamentos atrasados porque o email se perde (`entrevista-financas.md ¶5`).

**Business invariants**

- Já declarados pelo dono e registados como `Confirmed` em `enquadramento.md#M-1..M-4` (R-00) — recibo obrigatório, limiar de aprovação (valor em disputa), taxa por quilómetro por deliberação, retenção legal de comprovativos. Não repetidos aqui como novas linhas.

**Structural constraints**

- OBSERVED — o ERP-X já tem uma interface para registar pagamentos a colaboradores, nunca usada para reembolsos (`nota-ti.md · §Nota do responsável de sistemas (sintético) ¶1`). `estrutural: interface de pagamentos do ERP-X existe, por explorar em Options`
- INFERRED — pode já existir licença de uma plataforma low-code no contrato corporativo, por confirmar com compras (`nota-ti.md ¶2`); base: declaração de memória do responsável de sistemas, não verificada.
- OBSERVED — não existe orçamento aprovado para este projecto; qualquer custo recorrente precisa de aprovação da administração (`nota-ti.md ¶3`) — liga ao `funding_gate = true` (`context.json`).

**Material user tasks**

- OBSERVED — colaborador: preencher a folha de cálculo por deslocação e anexar fotografias dos recibos (introdução de dados manual) (`entrevista-financas.md ¶1`).
- OBSERVED — contabilidade: copiar valores entre folhas e depois para o ERP-X (re-introdução manual, fonte potencial de erro) (`entrevista-financas.md ¶1`).

**Genuine vs accidental complexity**

- HYPOTHESIS — a dupla cópia (folha do colaborador → outra folha → ERP-X) parece acidente de integração, não uma exigência de negócio; nenhuma fonte confirma necessidade de negócio para a folha intermédia. `processo: folha intermédia pode ser acidente de integração, não requisito`

**Material unresolved semantics**

- UNKNOWN — limiar de aprovação real, 250€ ou 500€ (`enquadramento.md#M-2`).
- UNKNOWN — taxa por quilómetro em vigor — depende de deliberação da administração não entregue (`enquadramento.md#M-3`). `regra: taxa por km sem valor confirmado`
- UNKNOWN — prazo de retenção legal aplicável, em número de anos (`enquadramento.md#M-4`). `operacao: prazo de retenção por saber`
- UNKNOWN — quem manda formalmente no processo (`enquadramento.md#T1`). (mesma linha que `processo: dono formal não identificado`, acima)
- UNKNOWN — critério de sucesso do processo (`enquadramento.md#T4`). (mesma linha que `Outputs sem critério de sucesso declarado`, acima)
- UNKNOWN — se existe já licença de plataforma low-code no contrato corporativo (`nota-ti.md ¶2`). `solucao: licença low-code por confirmar`
- UNKNOWN — horas por semana e custo agregado do trabalho manual da contabilidade — dados de entrada para a baseline financeira, não uma pergunta em si (`entrevista-financas.md ¶4`, ¶5; ver `library/kernel/states.md` → *Cost questions*: a lente financeira constrói a baseline como `Assumed`, não pergunta isto como `Unknown`).

## 4bis. Cadeia de cálculo (por saída)

`calc-chain: absent (sem fonte estruturada nesta captura — nenhum ficheiro `.xlsx`/`.xlsm` em `inputs/`)`

## 5. Anomalies & silent failures

Não aplicável — sem fonte estruturada, não há replay nem fórmulas a reportar. 0 anomalias de fórmula (não por ausência de leitura — por ausência do tipo de fonte).

## 6. Interrogation list (PM-U-NNN)

| id | question | why it matters | suggested respondent (role) | criticidade | custo | swing | classe | tipo | impacto |
|---|---|---|---|---|---|---|---|---|---|
| PM-U-001 | Qual é o limiar real de aprovação — 250€ (política escrita, `politica-rh.md#R1`) ou 500€ (dito pela contabilidade, `entrevista-financas.md#F3`)? | Define quem aprova cada pedido — regra de negócio central e critério de aceitação testável; as duas fontes discordam e o próprio dono não sabe qual vale | `role: director financeiro` (nomeado pelo dono em `enquadramento.md` para este tema) | Critical | email | dimensionante: define o desenho do passo de aprovação e o critério de aceitação, sem eliminar nenhuma opção de solução | processo | conflict | funcional, aceitacao: determina que perfil aprova cada pedido, e é critério de aceitação testável |
| PM-U-002 | Qual é a taxa por quilómetro em vigor, e onde está a deliberação da administração que a fixa (`politica-rh.md#R3`)? | Sem o valor não há fórmula completa para calcular o reembolso de deslocações em viatura própria | `role: administração` (nomeada pelo dono para orçamento e taxa/km) | Critical | documento | dimensionante: sem o valor não se especifica o cálculo do reembolso em viatura própria | processo | fact_gap | funcional: falta o valor/fonte para calcular o reembolso em viatura própria |
| PM-U-003 | Existem já licenças de alguma plataforma low-code no contrato corporativo (`nota-ti.md#T2`)? | Se existirem, muda o custo de uma opção "construir"; se não, essa opção implica licenciamento novo — afecta viabilidade e ordem de grandeza de pelo menos uma opção que o próprio pedido nomeia | `role: compras` (nomeada pelo dono para este tema) | Critical | email | decisivo: sem licença, a opção de construir na plataforma low-code muda de base de custo — pode deixar de ser a mesma opção tal como descrita | processo | fact_gap | solucao, viabilidade: determina se "construir" tem custo de licenciamento zero ou novo |
| PM-U-004 | Quem manda formalmente neste processo — dono operacional/orçamental — já que a contabilidade não o soube dizer (`enquadramento.md#T1`)? | Sem dono declarado falta autoridade clara para aprovar mudanças ao processo e para se responsabilizar pelo resultado | `role: directora administrativa` (a dona do pedido, a esclarecer ou delegar) | Med | email | dimensionante: define quem tem autoridade para aceitar o resultado e pedir mudanças depois de entregue | processo | fact_gap | operacao: falta o dono operacional/orçamental formal do processo |
| PM-U-005 | Como se sabe hoje que um pedido de reembolso "correu bem" — que critério de sucesso se usa (`enquadramento.md#T4`)? | Sem critério declarado não há forma de desenhar aceitação nem medir melhoria face ao actual | `role: direcção financeira` / `role: contabilidade` (a esclarecer) | Med | reuniao | dimensionante: define o critério de aceitação e de sucesso da solução | processo | fact_gap | aceitacao: falta o critério de sucesso do processo, logo falta o critério de aceitação da solução |

## 7. Not captured

Não aplicável a falha de extracção — as quatro fontes de texto extraíram-se por completo (`status: ok`); nenhuma falhou, foi saltada ou ficou parcialmente ilegível.

Artefactos nomeados na entrevista mas nunca entregues (não é falha de extracção — é ausência de entrega, já registada em `enquadramento.md` → *Ficheiros nomeados, ainda não entregues*, passo 4d2): a folha de cálculo de reembolso (modelo ou exemplo preenchido), o ERP-X (acesso/exportação/documentação), e a deliberação da administração que fixa a taxa por quilómetro.
