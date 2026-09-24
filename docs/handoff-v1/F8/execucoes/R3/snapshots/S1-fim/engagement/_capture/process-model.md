# Process Model — f8-r3-fx02

> Sources: pedido.md (a7da9323), entrevista-processo.md (8a709386), matriz-papeis.md (be7ebaa5), nota-dados.md (990dc582)  |  Generated: 2026-09-24T10:32:00Z  |  Capture run: 1
> Source dispositions: pedido.md USED · entrevista-processo.md USED · matriz-papeis.md USED · nota-dados.md USED

## 1. File map

- `pedido.md` — o pedido sintético do dono do processo (director de SI): âmbito, plataforma imposta, autoridade. USED — todo o ficheiro é material (5 parágrafos).
- `entrevista-processo.md` — notas de entrevista ao responsável de compras: o fluxo tal como corre hoje, as suas excepções e falhas. USED — todo o ficheiro é material (7 parágrafos).
- `matriz-papeis.md` — papéis e permissões pretendidos para o novo sistema. USED — todo o ficheiro é material (5 parágrafos).
- `nota-dados.md` — onde vivem os dados hoje (catálogo, pedidos, retenção). USED — todo o ficheiro é material (3 parágrafos).

Nenhuma fonte estruturada (`.xlsx`/`.xlsm`) neste engagement — todas as quatro fontes são texto (`.md`, tier capture-lite).

## 2. Column classification

Não se aplica — sem fonte estruturada.

## 3. Business rules (PM-NNN)

Não se aplica — sem fonte estruturada (sem fórmula, validação ou formatação condicional para provar `Confirmed`/`Assumed`). As regras de negócio observadas nas fontes de texto entram em §4, com o marcador epistémico e o locator do texto, não aqui.

## 4. Process synopsis (cross-source)

**Purpose**

- OBSERVED — `Process purpose` decidir e registar pedidos de equipamento informático (portáteis, monitores, acessórios) desde o pedido do colaborador até à encomenda em compras (pedido.md · §Pedido (sintético) ¶3, ¶4).

**End-to-end flow**

- OBSERVED — `chain: pedido → aprovação → registo/encomenda`: (1) colaborador pede equipamento por email; (2) chefia responde "aprovado" (ou rejeita); (3) compras regista o pedido numa folha de cálculo e encomenda; (4) acima de um limiar (definido num despacho não entregue) o pedido tem de ir primeiro à direcção financeira (entrevista-processo.md · §Notas de entrevista ¶1, ¶4).

**Actors**

- OBSERVED — requerente (cria/consulta os seus pedidos); chefia (aprova/rejeita os pedidos da sua equipa, nunca os seus próprios); compras (vê pedidos aprovados, regista a encomenda); direcção financeira (aprova acima do limiar); auditoria interna (consulta quem aprovou o quê e quando) (matriz-papeis.md · §Papéis e permissões pretendidos ¶1-¶5).
- UNKNOWN — quem manda formalmente no processo (dono último) — ver PM-U-004 (pedido.md, entrevista-processo.md não dizem).

**Inputs**

- OBSERVED — pedido do colaborador, por email, sem formulário estruturado hoje (manual, ad-hoc) (entrevista-processo.md ¶1).
- OBSERVED — `Inputs catalog` catálogo de equipamento com preços em vigor vive no ERP-X; a folha de compras guarda uma cópia actualizada à mão "quando alguém se lembra" — risco de desactualização (nota-dados.md ¶1).

**Transformation / calculation stages**

- OBSERVED — `chain: linhas do pedido → valor do pedido`: quantidade × preço unitário por linha, somado, mais IVA à taxa normal (entrevista-processo.md ¶2).
- UNKNOWN — ponto exacto do arredondamento ao cêntimo (linha a linha ou só no total) — já causou diferenças de um cêntimo com a contabilidade — ver PM-U-001 (entrevista-processo.md ¶3).

**Intermediate state**

- INFERRED — valor do pedido (antes de IVA) e valor final (com IVA) são estados intermédios entre as linhas do pedido e a decisão de aprovação/routing; base: o valor determina se o pedido segue só para a chefia ou também para a direcção financeira (entrevista-processo.md ¶2, ¶4).

**Decisions**

- OBSERVED — a chefia decide aprovar/rejeitar (regra: nunca o seu próprio pedido — M-1). Em avaria urgente, compras encomenda primeiro e a chefia valida depois, no mesmo dia — excepção ao fluxo normal de aprovação prévia (entrevista-processo.md ¶4, ¶5; matriz-papeis.md ¶2, ¶4).
- UNKNOWN — valor exacto do limiar que faz a direcção financeira decidir (aprovar) — ver PM-U-002 (entrevista-processo.md ¶4).

**Outputs and consumers**

- OBSERVED — `Outputs encomenda` a encomenda registada por compras, que despoleta a compra do equipamento; consumidor imediato: compras/fornecedor (pedido.md ¶4; entrevista-processo.md ¶1).
- UNKNOWN — como se sabe que o processo "correu bem" (critério de sucesso) — ver PM-U-006 (pedido.md, entrevista-processo.md não dizem).
- HYPOTHESIS — `Outputs auditoria` registo de quem aprovou o quê e quando, consumido pela auditoria interna, ainda não existe de forma fiável hoje (email + folha de cálculo não garantem rastreio consistente); a confirmar em `/round` (matriz-papeis.md ¶5).

**Variants**

- OBSERVED — pedido normal (aprovação prévia da chefia, e da direcção financeira acima do limiar) vs pedido urgente por avaria (encomenda primeiro, validação da chefia no mesmo dia) (entrevista-processo.md ¶5).

**Exceptions and workarounds**

- OBSERVED — `Exceptions duplicado` pedidos duplicados: a mesma pessoa reenvia o mesmo pedido por achar que o email não chegou, e compras encomenda a dobrar — falha de hoje, sem mecanismo de detecção (entrevista-processo.md ¶6).
- OBSERVED — `Exceptions catalogo-desactualizado` cópia do catálogo na folha de compras desactualizada por depender de alguém se lembrar de a actualizar (nota-dados.md ¶1).

**Business invariants**

- OBSERVED — `chefia nunca aprova pedido próprio` (M-1) (matriz-papeis.md ¶2).
- OBSERVED — `acima do limiar do despacho vai à direcção financeira` (M-2) (matriz-papeis.md ¶4; entrevista-processo.md ¶4).
- OBSERVED — `auditoria tem de ver quem aprovou o quê e quando` (M-3) (matriz-papeis.md ¶5).
- OBSERVED — `documentos de compra conservados 10 anos` (M-4) (nota-dados.md ¶3).

  Todos os quatro já `Confirmed` na Shared Understanding via enquadramento (R-00) — replicados aqui como evidência cruzada, não como novidade.

**Structural constraints**

- HYPOTHESIS — `Structural constraints catalogo` qualquer solução terá de decidir se lê preços em tempo real do ERP-X ou mantém cópia própria (como a folha de compras faz hoje, com o risco de desactualização já observado) — ver PM-U-003 (nota-dados.md ¶1).

**Material user tasks**

- OBSERVED — hoje: escrever um email (requerente); responder "aprovado"/"rejeitado" por email (chefia); transcrever para folha de cálculo e encomendar (compras). Nenhuma tarefa estruturada de ecrã existe ainda (entrevista-processo.md ¶1).

**Genuine vs accidental complexity**

- HYPOTHESIS — a duplicação de pedidos e a desactualização do catálogo parecem acidentais — consequência do meio (email, cópia manual), não uma exigência do negócio; a confirmar em `/round` (entrevista-processo.md ¶6; nota-dados.md ¶1).
- INFERRED — a distinção entre pedido normal e urgente, e o limiar de aprovação financeira, parecem genuínos — servem um invariante de controlo (M-1, M-2) (entrevista-processo.md ¶4, ¶5).

**Material unresolved semantics**

- UNKNOWN — ponto de arredondamento (linha a linha vs total) — ver PM-U-001.
- UNKNOWN — valor do limiar de aprovação financeira — ver PM-U-002.
- UNKNOWN — autoridade formal do processo (dono último) — ver PM-U-004.

## 4bis. Cadeia de cálculo (por saída)

calc-chain: absent (sem fonte estruturada — nenhum workbook neste engagement)

## 5. Anomalies & silent failures

Não se aplica — sem replay (sem fonte estruturada).

## 6. Interrogation list (PM-U-NNN)

| id | question | why it matters | suggested respondent (role) | criticidade | custo | swing | classe | tipo | impacto |
|---|---|---|---|---|---|---|---|---|---|
| PM-U-001 | O arredondamento ao cêntimo é aplicado linha a linha ou só no total do pedido? | Já causou diferenças de um cêntimo com a contabilidade; decide a regra de cálculo do valor do pedido, que gate de aprovação (limiar) usa. | `role: responsável de compras` \| `fonte: entrevista-processo.md ¶3` | Med | reuniao | dimensionante — muda a regra de cálculo do valor do pedido e, por consequência, quando o limiar é ultrapassado | dados | conflict | funcional |
| PM-U-002 | Qual é o valor exacto do limiar acima do qual o pedido tem de ir à direcção financeira, e como está definido (despacho)? | Sem este valor, a regra de routing para a direcção financeira (M-2) não pode ser implementada; artefacto "despacho" ainda não entregue. | `role: direcção financeira` \| `fonte: despacho (não entregue)` | Critical | documento | decisivo — sem o valor, o fluxo de aprovação financeira não pode ser desenhado nem testado | processo | fact_gap | funcional, aceitacao |
| PM-U-003 | O novo sistema deve ler os preços em tempo real do ERP-X, ou manter uma cópia própria dos preços (como a folha de compras faz hoje)? | Decide se há integração com o ERP-X ou duplicação de dados com risco de desactualização (já observado hoje). | `role: director de sistemas de informação` \| `fonte: nota-dados.md ¶1` | Med | reuniao | dimensionante — muda o modelo de dados e o plano de integração | dados | design_choice | funcional, operacao |
| PM-U-004 | Quem manda formalmente no processo — quem é o dono/responsável último pelo fluxo pedido→aprovação→compra? | Sem um dono formal identificado, a autoridade para resolver conflitos e aprovar mudanças ao processo fica em aberto. | `role: director de sistemas de informação` \| `fonte: enquadramento.md#T1` | Low | reuniao | cosmético — não muda desenho nem esforço, só clarifica um contacto de governação | processo | fact_gap | aceitacao |
| PM-U-005 | Com que frequência ocorre este processo (pedidos por dia/semana/mês)? | Dimensiona o esforço e o volume que o desenho tem de suportar. | `role: responsável de compras` \| `fonte: enquadramento.md#T2` | Low | email | dimensionante — muda a estimativa de esforço/dimensionamento | processo | fact_gap | operacao |
| PM-U-006 | Como se sabe que o processo "correu bem" — qual é o critério de sucesso do pedido? | Sem critério de sucesso declarado, a aceitação do desenho final não tem padrão contra o qual validar. | `role: director de sistemas de informação` \| `fonte: enquadramento.md#T4` | Med | reuniao | dimensionante — define o critério de aceitação do desenho | processo | fact_gap | aceitacao |

## 7. Not captured

Nada foi excluído por protecção, macro ou formato ilegível — todas as quatro fontes de texto extraíram com `status: ok`. Não há fonte estruturada (`.xlsx`/`.xlsm`) neste engagement, logo não há VBA, ligações externas, folhas protegidas ou fórmulas não replayable a listar. O único artefacto nomeado e não entregue é o "despacho" que define o limiar de aprovação financeira (enquadramento.md, passo 4d2) — evidência **inacessível** por agora (ficheiro não entregue), registado como `Unknown` (PM-U-002), não como `TO-READ` (não há ficheiro legível ainda por ler).
