# Process Model — f8-r3-fx02

> Sources: pedido.md (a7da9323), entrevista-processo.md (8a709386), matriz-papeis.md (be7ebaa5), nota-dados.md (990dc582), nota-urgentes.md (44e9eab9), mudancas.md (eba5ccb7)  |  Generated: 2026-09-24T16:35:00Z  |  Capture run: 3
> Source dispositions: pedido.md CHECKED · entrevista-processo.md CHECKED · matriz-papeis.md CHECKED · nota-dados.md CHECKED · nota-urgentes.md CHECKED · mudancas.md USED

## 1. File map

- `pedido.md` — o pedido sintético do dono do processo (director de SI): âmbito, plataforma imposta, autoridade. CHECKED — sem mudança desde o run 2; conteúdo já reconstruído (5 parágrafos).
- `entrevista-processo.md` — notas de entrevista ao responsável de compras: o fluxo tal como corre hoje, as suas excepções e falhas. CHECKED — sem mudança desde o run 2 (7 parágrafos).
- `matriz-papeis.md` — papéis e permissões pretendidos para o novo sistema. CHECKED — sem mudança desde o run 2 (5 parágrafos).
- `nota-dados.md` — onde vivem os dados hoje (catálogo, pedidos, retenção). CHECKED — sem mudança desde o run 2 (3 parágrafos).
- `nota-urgentes.md` — nota do responsável de compras, datada 2026-10-01, sobre o caminho de urgência. CHECKED — sem mudança desde o run 2 (3 parágrafos).
- `mudancas.md` — nota síntese do cliente, entregue depois do handoff aprovado (D-002), com três mudanças de negócio pós-aprovação. USED — todo o ficheiro é material (3 parágrafos): [X1] regra de arredondamento nova; [X2] correcção de gralha na descrição da jornada de pedido, sem mudança de significado; [X3] novo despacho baixa o limiar da direcção financeira.

Nenhuma fonte estruturada (`.xlsx`/`.xlsm`) neste engagement — todas as seis fontes são texto (`.md`, tier capture-lite).

## 2. Column classification

Não se aplica — sem fonte estruturada.

## 3. Business rules (PM-NNN)

Não se aplica — sem fonte estruturada (sem fórmula, validação ou formatação condicional para provar `Confirmed`/`Assumed`). As regras de negócio observadas nas fontes de texto entram em §4, com o marcador epistémico e o locator do texto, não aqui.

## 4. Process synopsis (cross-source)

**Purpose**

- OBSERVED — `Process purpose` decidir e registar pedidos de equipamento informático (portáteis, monitores, acessórios) desde o pedido do colaborador até à encomenda em compras (pedido.md · §Pedido (sintético) ¶3, ¶4).

**End-to-end flow**

- OBSERVED — `chain: pedido → aprovação → registo/encomenda`: (1) colaborador pede equipamento por email; (2) chefia responde "aprovado" (ou rejeita); (3) compras regista o pedido numa folha de cálculo e encomenda; (4) acima do limiar da direcção financeira o pedido tem de ir primeiro à direcção financeira (entrevista-processo.md · §Notas de entrevista ¶1, ¶4).

**Actors**

- OBSERVED — requerente (cria/consulta os seus pedidos); chefia (aprova/rejeita os pedidos da sua equipa, nunca os seus próprios); compras (vê pedidos aprovados, regista a encomenda); direcção financeira (aprova acima do limiar); auditoria interna (consulta quem aprovou o quê e quando) (matriz-papeis.md · §Papéis e permissões pretendidos ¶1-¶5).
- UNKNOWN — quem manda formalmente no processo (dono último) — ver PM-U-004 (pedido.md, entrevista-processo.md não dizem).

**Inputs**

- OBSERVED — pedido do colaborador, por email, sem formulário estruturado hoje (manual, ad-hoc) (entrevista-processo.md ¶1).
- OBSERVED — `Inputs catalog` catálogo de equipamento com preços em vigor vive no ERP-X; a folha de compras guarda uma cópia actualizada à mão "quando alguém se lembra" — risco de desactualização (nota-dados.md ¶1).

**Transformation / calculation stages**

- OBSERVED — `chain: linhas do pedido → valor do pedido`: quantidade × preço unitário por linha, somado, mais IVA à taxa normal (entrevista-processo.md ¶2).
- OBSERVED — ponto do arredondamento ao cêntimo: **muda pós-aprovação (X1)** — a contabilidade decide que passa a ser aplicado linha a linha, pela regra meio-para-o-par (banker's rounding), para alinhar com a facturação do fornecedor; substitui a regra anteriormente confirmada (Shared Understanding C-007: só ao total, meio-para-cima) (mudancas.md ¶1). PM-U-001 (o ponto de arredondamento era Unknown) fica retirado por esta nota — a pergunta está definitivamente respondida, agora por uma segunda vez; ver §6.

**Intermediate state**

- INFERRED — valor do pedido (antes de IVA) e valor final (com IVA) são estados intermédios entre as linhas do pedido e a decisão de aprovação/routing; base: o valor determina se o pedido segue só para a chefia ou também para a direcção financeira (entrevista-processo.md ¶2, ¶4).

**Decisions**

- OBSERVED — a chefia decide aprovar/rejeitar (regra: nunca o seu próprio pedido — M-1). Em avaria urgente, compras encomenda primeiro; o prazo para a chefia validar depois já não é o mesmo dia — mudou para o fim do dia útil seguinte (nota-urgentes.md ¶2) — excepção ao fluxo normal de aprovação prévia (matriz-papeis.md ¶2, ¶4).
- OBSERVED — se a chefia não validar dentro desse prazo (fim do dia útil seguinte), compras suspende a encomenda até haver validação (nota-urgentes.md ¶3).
- OBSERVED — o limiar acima do qual o pedido tem de ir à direcção financeira **muda pós-aprovação (X3)**: novo despacho baixa-o de 5 000 € para 3 000 € (mudancas.md ¶3); substitui o valor anteriormente confirmado (Shared Understanding C-006 = 5 000 €). PM-U-002 (o valor exacto do limiar era Unknown) fica retirado por esta nota — a pergunta está definitivamente respondida, agora por uma segunda vez; ver §6. **Efeito material**: um limiar mais baixo alarga o conjunto de pedidos que cruzam a fronteira da aprovação financeira — inclui, potencialmente, mais pedidos urgentes; o conflito já registado (X-001 na Shared Understanding — o caminho de urgência salta ou não a aprovação financeira acima do limiar) mantém-se aberto e materialmente mais pesado com o limiar mais baixo, mas mudancas.md não o resolve.
- OBSERVED — correcção editorial (X2): a descrição da jornada de pedido tinha uma gralha ("encomeda"), corrigida para "encomenda"; o próprio cliente declara "sem mudança de significado" (mudancas.md ¶2). Nenhuma fonte deste engagement contém a grafia antiga — não se localizou o texto a corrigir dentro do que este processo captura; sem consequência de processo, sem PM-U, sem linha na Shared Understanding (sem impacto demonstrável nos cinco aspectos de admissão).
- UNKNOWN — nota-urgentes.md não diz se o caminho de urgência, com o novo prazo alargado, também passa a saltar (ou não) a aprovação da direcção financeira quando o pedido urgente ultrapassa o limiar do despacho — o conflito já registado (X-001 na Shared Understanding) mantém-se aberto, sem resposta nesta nota nem em mudancas.md.

**Outputs and consumers**

- OBSERVED — `Outputs encomenda` a encomenda registada por compras, que despoleta a compra do equipamento; consumidor imediato: compras/fornecedor (pedido.md ¶4; entrevista-processo.md ¶1).
- UNKNOWN — como se sabe que o processo "correu bem" (critério de sucesso) — ver PM-U-006 (pedido.md, entrevista-processo.md não dizem).
- HYPOTHESIS — `Outputs auditoria` registo de quem aprovou o quê e quando, consumido pela auditoria interna, ainda não existe de forma fiável hoje (email + folha de cálculo não garantem rastreio consistente); a confirmar em `/round` (matriz-papeis.md ¶5).

**Variants**

- OBSERVED — pedido normal (aprovação prévia da chefia, e da direcção financeira acima do limiar) vs pedido urgente por avaria (encomenda primeiro; validação da chefia agora até ao fim do dia útil seguinte, já não no mesmo dia; sem validação nesse prazo, compras suspende a encomenda) (entrevista-processo.md ¶5; nota-urgentes.md ¶2, ¶3).

**Exceptions and workarounds**

- OBSERVED — `Exceptions duplicado` pedidos duplicados: a mesma pessoa reenvia o mesmo pedido por achar que o email não chegou, e compras encomenda a dobrar — falha de hoje, sem mecanismo de detecção (entrevista-processo.md ¶6).
- OBSERVED — `Exceptions catalogo-desactualizado` cópia do catálogo na folha de compras desactualizada por depender de alguém se lembrar de a actualizar (nota-dados.md ¶1).

**Business invariants**

- OBSERVED — `chefia nunca aprova pedido próprio` (M-1) (matriz-papeis.md ¶2).
- OBSERVED — `acima do limiar do despacho vai à direcção financeira` (M-2) (matriz-papeis.md ¶4; entrevista-processo.md ¶4). O invariante em si não muda com X3 — só o valor do limiar (C-006) muda.
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

- UNKNOWN — autoridade formal do processo (dono último) — ver PM-U-004.
- UNKNOWN — o que "suspende a encomenda" significa mecanicamente no caminho de urgência — ver PM-U-007.
- UNKNOWN — se o caminho de urgência, com o prazo alargado, salta a aprovação da direcção financeira acima do limiar — conflito já registado como X-001 na Shared Understanding; nem nota-urgentes.md nem mudancas.md o resolvem. Materialidade aumentada por X3 (limiar mais baixo).

  (O ponto de arredondamento e o valor do limiar saíram desta lista — mudancas.md observa-os directamente; deixaram de ser semântica por resolver. Ver linhas OBSERVED em **Transformation** e **Decisions**, acima.)

## 4bis. Cadeia de cálculo (por saída)

calc-chain: absent (sem fonte estruturada — nenhum workbook neste engagement)

## 5. Anomalies & silent failures

Não se aplica — sem replay (sem fonte estruturada).

## 6. Interrogation list (PM-U-NNN)

| id | question | why it matters | suggested respondent (role) | criticidade | custo | swing | classe | tipo | impacto |
|---|---|---|---|---|---|---|---|---|---|
| PM-U-003 | O novo sistema deve ler os preços em tempo real do ERP-X, ou manter uma cópia própria dos preços (como a folha de compras faz hoje)? | Decide se há integração com o ERP-X ou duplicação de dados com risco de desactualização (já observado hoje). | `role: director de sistemas de informação` \| `fonte: nota-dados.md ¶1` | Med | reuniao | dimensionante — muda o modelo de dados e o plano de integração | dados | design_choice | funcional, operacao |
| PM-U-004 | Quem manda formalmente no processo — quem é o dono/responsável último pelo fluxo pedido→aprovação→compra? | Sem um dono formal identificado, a autoridade para resolver conflitos e aprovar mudanças ao processo fica em aberto. | `role: director de sistemas de informação` \| `fonte: enquadramento.md#T1` | Low | reuniao | cosmético — não muda desenho nem esforço, só clarifica um contacto de governação | processo | fact_gap | aceitacao |
| PM-U-005 | Com que frequência ocorre este processo (pedidos por dia/semana/mês)? | Dimensiona o esforço e o volume que o desenho tem de suportar. | `role: responsável de compras` \| `fonte: enquadramento.md#T2` | Low | email | dimensionante — muda a estimativa de esforço/dimensionamento | processo | fact_gap | operacao |
| PM-U-006 | Como se sabe que o processo "correu bem" — qual é o critério de sucesso do pedido? | Sem critério de sucesso declarado, a aceitação do desenho final não tem padrão contra o qual validar. | `role: director de sistemas de informação` \| `fonte: enquadramento.md#T4` | Med | reuniao | dimensionante — define o critério de aceitação do desenho | processo | fact_gap | aceitacao |
| PM-U-007 | "Compras suspende a encomenda até haver validação" (nota-urgentes.md ¶3, urgentes) — significa que a encomenda não chega a ser enviada ao fornecedor enquanto não há validação (estado interno, pendente), ou que uma encomenda já enviada é cancelada/pausada junto do fornecedor? | Muda o modelo de estados da encomenda e se há um passo externo (cancelamento junto do fornecedor) a desenhar — TO-BE DIVERGENCE: o dono tem de dizer qual dos dois mecanismos quer. | `role: responsável de compras` \| `fonte: nota-urgentes.md ¶3` | Med | email | dimensionante (eixo componentes, modelo de dados) — estado interno pendente vs cancelamento externo junto do fornecedor — muda o modelo de estados da encomenda e pode acrescentar um passo de integração | processo | design_choice | funcional |

**Retirados neste run (3)**: `PM-U-001` (ponto de arredondamento) e `PM-U-002` (valor do limiar) — ambos já tinham resposta na Shared Understanding (C-007, was U-003; C-006, was U-005) antes deste run, e `mudancas.md` agora observa directamente os dois factos de novo (X1, X3), desta vez superando as respostas anteriores. A pergunta original de cada um está definitivamente fechada — não reabre como PM-U; a mudança de valor entra como facto OBSERVED em §4 e segue para a Shared Understanding pela síntese da passagem de Options que processa esta reabertura, nunca como pergunta nova. Ids nunca reutilizados.

## 7. Not captured

Nada foi excluído por protecção, macro ou formato ilegível — todas as seis fontes de texto extraíram com `status: ok`. Não há fonte estruturada (`.xlsx`/`.xlsm`) neste engagement, logo não há VBA, ligações externas, folhas protegidas ou fórmulas não replayable a listar. O único artefacto nomeado e não entregue é o "despacho" que definia o limiar anterior (enquadramento.md, passo 4d2) — resolvido entretanto (C-006) e agora substituído por um despacho mais recente (X3, mudancas.md ¶3), este também não entregue como ficheiro — o valor vem declarado em mudancas.md, não de um documento do despacho em si.

A gralha que mudancas.md ¶2 (X2) diz corrigir ("encomeda" → "encomenda", na descrição da jornada de pedido) não foi localizada em nenhuma fonte deste engagement (`inputs/`, `_capture/`, `shared-understanding.md`, `decisions.md`, `options.md`) — o texto original com a gralha não é evidência capturada aqui. Registado como declarado pelo cliente, sem consequência de processo (o próprio X2 diz "sem mudança de significado"); não gera PM-U nem linha na Shared Understanding, por não haver impacto demonstrável.
