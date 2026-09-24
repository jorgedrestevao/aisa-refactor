# Shared Understanding — f8-r3-fx02

> Engagement: f8-r3-fx02
> Sponsor: Director de Sistemas de Informação, Organização Exemplo
> Iniciado: 2026-09-24
> Fase actual: Framing
> Última actualização: 2026-09-24T12:00:00Z

## Confirmed

| id | lens | claim | evidência | verificado_em | validade | ronda |
|----|------|-------|-----------|---------------|----------|-------|
| C-001 | enquadramento | O dono declara que a plataforma Power Platform foi decidida por director de sistemas de informação. | declaração do dono do processo, 2026-09-24 — answers.md#ROTA | 2026-09-24 | organizacional | R-00 |
| M-1 | enquadramento | A chefia nunca aprova um pedido feito por si própria. | declaração do dono do processo, 2026-09-24 — enquadramento.md#M-1 | 2026-09-24 | organizacional | R-00 |
| M-2 | enquadramento | Acima do limiar definido em despacho, o pedido tem de ir à direcção financeira. | declaração do dono do processo, 2026-09-24 — enquadramento.md#M-2 | 2026-09-24 | organizacional | R-00 |
| M-3 | enquadramento | A auditoria interna tem de saber quem aprovou o quê e quando. | declaração do dono do processo, 2026-09-24 — enquadramento.md#M-3 | 2026-09-24 | organizacional | R-00 |
| M-4 | enquadramento | Os documentos de compra são conservados 10 anos. | declaração do dono do processo, 2026-09-24 — enquadramento.md#M-4 | 2026-09-24 | organizacional | R-00 |
| C-002 | operations | Hoje, o colaborador pede equipamento por email; a chefia aprova ou rejeita; compras regista o pedido numa folha de cálculo e faz a encomenda. | entrevista-processo.md · ¶1; matriz-papeis.md · ¶2 | 2026-09-24 | organizacional | R-01 |
| C-003 | operations | Pedidos urgentes (avaria que impede trabalhar) vão directamente a compras; a chefia valida depois, no mesmo dia. | entrevista-processo.md · ¶5 | 2026-09-24 | organizacional | R-01 |
| C-004 | data | O catálogo de equipamento com preços em vigor vive hoje no ERP-X; a folha de compras mantém uma cópia actualizada à mão. | nota-dados.md · ¶1 | 2026-09-24 | organizacional | R-01 |
| C-005 | data | O valor do pedido é a soma de quantidade × preço unitário de cada linha, mais IVA à taxa normal. | entrevista-processo.md · ¶2 | 2026-09-24 | financeiro | R-01 |
| C-006 | governance | O limiar acima do qual o pedido tem de ir à direcção financeira é 5 000 € por pedido (valor definido no despacho). | USER_ANSWER 2026-09-24 — direcção financeira (was U-005), answers.md#U-005 | 2026-09-24 | organizacional | R-01 |
| C-007 | data | O arredondamento é aplicado só ao total do pedido, ao cêntimo, pela regra meio-para-cima. | USER_ANSWER 2026-09-24 — responsável de compras (was U-003), answers.md#U-003 | 2026-09-24 | organizacional | R-01 |
| C-008 | chair | O âmbito autorizado cobre o pedido, a aprovação e a passagem a compras; gestão de stock e recepção física ficam fora. | declaração do dono do processo (director de sistemas de informação), 2026-09-02 — pedido.md · ¶4 | 2026-09-24 | organizacional | F-01 |

## Assumed

| id | lens | claim | base da assumption | verificado_em | validade | ronda |
|----|------|-------|--------------------|---------------|----------|-------|
| A-001 | business | O impacto declarado (pedidos duplicados, divergências de arredondamento) é qualitativo — sem medição de frequência ou custo. | relato do responsável de compras, sem números — entrevista-processo.md · ¶3, ¶6 | 2026-09-24 | organizacional | R-01 |
| A-002 | user | O requerente precisa de confirmação visível de que o pedido foi recebido, para não reenviar por dúvida — causa observada dos pedidos duplicados. | inferência razoável a partir de "acha que o email não chegou" — entrevista-processo.md · ¶6 | 2026-09-24 | organizacional | R-01 |
| A-003 | data | Hoje não existe um sistema único de registo dos pedidos — vivem dispersos entre email e a folha de cálculo de compras. | nota-dados.md · ¶2; entrevista-processo.md · ¶1 | 2026-09-24 | organizacional | R-01 |
| A-004 | financial | O custo de não fazer nada é qualitativo: inclui encomendas duplicadas e divergências de arredondamento com a contabilidade, sem valor monetário medido. | entrevista-processo.md · ¶3, ¶6 | 2026-09-24 | organizacional | R-01 |
| A-005 | financial | O custo do actual processo (não fazer nada) tem a forma: custo = volume de pedidos × tempo perdido por pedido × taxa horária carregada + custo dos pedidos duplicados + custo das divergências de arredondamento com a contabilidade. Nenhum dos factores (volume, tempo por passo, taxa) está hoje medido. | estrutura de custo derivada dos factores observados (entrevista-processo.md · ¶3, ¶6); nenhum valor vem do cliente — os três factores ficam Unknown: U-001 (volume), U-009 (tempo por passo), U-010 (taxa horária carregada) | 2026-09-24 | organizacional | R-01 |

## Unknown

| id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | ronda |
|----|------|----------|------|---------|--------|---------------|-------|----------|-------------|-------|-------|-------------|-------|
| U-001 | operations | Com que frequência ocorre este processo (pedidos por dia/semana/mês)? | fact_gap | solucao: dimensiona o esforço e o tamanho do desenho pelo volume real de pedidos | dimensionamento do esforço (observed_as_is) | role: responsável de compras | resposta do responsável de compras sobre o volume mensal/semanal | — | Low | email | dimensionante: muda a estimativa de esforço (volume de pedidos a suportar) | PM-U-005 | R-01 |
| U-002 | user | Em que contexto os colaboradores fazem hoje o pedido (secretária, terreno, dispositivo, ligação)? | fact_gap | funcional: muda o desenho da interacção e o que o ecrã tem de suportar | desenho da interacção do pedido (proposed_to_be) | role: requerente | levantamento junto de uma amostra de requerentes | delegated_choice | Med | reuniao | dimensionante: muda o desenho da interacção e o que o ecrã tem de suportar | matriz-papeis.md | R-01 |
| U-003 | data | O arredondamento ao cêntimo é aplicado linha a linha ou só no total do pedido? | design_choice | funcional: muda a regra de cálculo do valor do pedido e o teste de aceitação financeiro | cálculo do valor do pedido (observed_as_is) | role: responsável de compras / role: contabilidade | definição da regra de arredondamento pelo dono/contabilidade | blocks_scope | Med | reuniao | dimensionante: arredondar linha a linha ou arredondar só no total — muda a regra de cálculo e o teste de aceitação financeiro | PM-U-001 | R-01 — resolved -> C-007 |
| U-004 | data | O novo sistema deve ler os preços em tempo real do ERP-X, ou manter uma cópia própria (como a folha de compras faz hoje)? | design_choice | solucao: muda o modelo de dados e o plano de integração com o ERP-X | arquitectura de dados do catálogo (proposed_to_be) | role: director de sistemas de informação | decisão do director de SI sobre a fonte de verdade dos preços | delegated_choice | Med | reuniao | dimensionante: ler preços em tempo real do ERP-X ou manter cópia própria sincronizada — muda o modelo de dados e o plano de integração | PM-U-003 | R-01 |
| U-005 | governance | Qual é o valor exacto do limiar acima do qual o pedido tem de ir à direcção financeira, e como está definido (despacho)? | fact_gap | funcional, aceitacao: sem o valor do limiar, o fluxo de aprovação financeira não pode ser desenhado nem testado | fluxo de aprovação financeira (observed_as_is) | fonte: despacho / role: direcção financeira | leitura do despacho (documento) quando entregue | blocks_scope | Critical | documento | dimensionante: sem o valor do limiar, o fluxo de aprovação financeira não pode ser desenhado nem testado | PM-U-002, M-2 | R-01 — resolved -> C-006 |
| U-006 | governance | Que mecanismo regista quem aprovou o quê e quando, de forma fiável (a auditoria exige-o e hoje não existe)? | design_choice | funcional, aceitacao: muda o desenho do mecanismo de registo de aprovações | mecanismo de auditoria (proposed_to_be) | role: auditoria interna / role: director de sistemas de informação | decisão de desenho do mecanismo de auditoria em blueprint | blocks_scope | Med | reuniao | dimensionante: registo automático pelo sistema ou campo de assinatura manual — muda o mecanismo de registo de aprovações | M-3 | R-01 |
| U-007 | financial | Qual é o envelope orçamental, o modelo de financiamento e o limiar de aprovação para este projecto? | fact_gap | viabilidade: muda a dimensão viável do projecto e o esforço que pode ser gasto | viabilidade orçamental do projecto (proposed_to_be) | role: direcção financeira / role: director de sistemas de informação | resposta da direcção financeira/director de SI sobre orçamento | blocks_all | Med | reuniao | dimensionante: muda a dimensão viável do projecto e o esforço que pode ser gasto | context.json#funding_gate | R-01 |
| U-008 | business | Como se sabe que este processo, e o projecto que o digitaliza, correu bem — qual é o critério de sucesso? | fact_gap | aceitacao: sem um critério, a aprovação final do desenho não tem padrão contra o qual validar | critério de aceitação do projecto (proposed_to_be) | role: director de sistemas de informação | decisão do dono sobre o critério de sucesso, em /decide ou /blueprint | blocks_scope | Med | reuniao | dimensionante: define o critério de aceitação do desenho final | PM-U-006, enquadramento.md#T4 | R-01 |
| U-009 | operations | Quanto tempo demora hoje cada passo do processo (pedir por email, aprovar, registar em compras e encomendar)? | fact_gap | solucao: alimenta a coluna de tempo do as-is e, por ela, a estimativa de esforço da mudança operacional | tempo por passo do as-is (observed_as_is) | role: responsável de compras / role: requerente | resposta de quem faz cada passo hoje, por passo | — | Low | email | dimensionante: muda o envelope de custo as-is (A-005) e a estimativa de esforço | entrevista-processo.md · ¶1 | R-01 |
| U-010 | financial | Qual é a taxa horária carregada de quem hoje faz cada passo (colaborador, chefia, compras)? | fact_gap | viabilidade: é o terceiro factor em falta para quantificar o envelope de custo as-is (A-005) | envelope de custo as-is (observed_as_is) | role: direcção financeira | resposta da direcção financeira/RH sobre a taxa carregada | — | Low | email | dimensionante: muda o valor quantificado do envelope de custo as-is | A-005 | R-01 |

## Conflicted

| id | lens | conflito | partes | impacto | âmbito | quem decide | fecho | bloqueio | criticidade | referências | ronda |
|----|------|----------|--------|---------|--------|-------------|-------|----------|-------------|-------------|-------|
| X-001 | governance | O caminho de urgência salta a aprovação prévia da chefia (valida só depois, no mesmo dia); não está declarado se também salta a aprovação da direcção financeira quando o pedido urgente ultrapassa o limiar do despacho. | operations∧governance | funcional, aceitacao: o caminho de urgência pode saltar o controlo financeiro sem que ninguém tenha decidido isso | fluxo de aprovação urgente (observed_as_is) | role: director de sistemas de informação | decisão do dono sobre a regra do caminho urgente face ao limiar financeiro | blocks_scope | Critical | M-1, M-2, entrevista-processo.md · ¶4, ¶5 | R-01 |

## Risky

| id | lens | risco | impacto | mitigação proposta | ronda |
|----|------|-------|---------|--------------------|-------|
| R-001 | operations | Pedidos duplicados por reenvio (o colaborador julga que o email não chegou) levam a encomendas a dobrar, sem mecanismo de detecção hoje. | desperdício financeiro e rework em compras | Detectar duplicados por regra (mesmo requerente + conteúdo semelhante + janela curta) antes de encomendar; dar confirmação visível ao requerente (ver A-002). | R-01 |
| R-002 | data | A cópia do catálogo de preços na folha de compras é actualizada à mão, sem cadência definida — risco de preços desactualizados na encomenda. | encomendas com preços errados; divergências financeiras | Decidir fonte única de verdade para preços entre ERP-X e o novo sistema (ver U-004). | R-01 |
