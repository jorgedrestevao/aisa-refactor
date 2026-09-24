## analista integrado — Round F-01 / Phase Framing

### Headline

O problema é a falta de um sistema único para pedir, aprovar e encomendar equipamento informático — hoje tudo corre por email e por uma folha de cálculo, sem confirmação de recepção nem preço sempre actualizado —, sentido por compras (retrabalho com encomendas a dobrar) e pela contabilidade (divergências de arredondamento); custa hoje pedidos duplicados e divergências reais já ocorridas, ainda sem envelope quantificado (falta o volume, o tempo por passo e a taxa horária carregada); a evidência vem da entrevista ao responsável de compras e da nota sobre os dados do catálogo.

### Evidence anchors

- O problema é (falta de sistema único, tudo por email/folha de cálculo) — source: C-002, A-003.
- Felt by (compras: retrabalho; contabilidade: arredondamento) — source: A-001, R-001.
- Costs today (pedidos duplicados, divergências de arredondamento; sem envelope quantificado) — source: A-001, A-004, A-005 (fórmula escrita, quantificação bloqueada por U-001, U-009, U-010).
- Evidence is (entrevista-processo.md, nota-dados.md) — source: entrevista-processo.md · §Notas de entrevista ¶1, ¶3, ¶6; nota-dados.md · §Nota sobre dados ¶1.
- M-1 (chefia nunca aprova pedido próprio) — confirmado, sem correcção — source: M-1.
- M-2 (acima do limiar vai à direcção financeira) — confirmado, sem correcção; valor do limiar já apurado (5 000 €) — source: M-2, C-006.
- M-3 (auditoria vê quem aprovou o quê e quando) — confirmado, sem correcção; mecanismo ainda por desenhar — source: M-3, U-006.
- M-4 (documentos de compra conservados 10 anos) — confirmado, sem correcção — source: M-4.

### Proposal

Candidatos a sobreviver até às Alternativas (`frame.md` → *O que tem de sobreviver*):

- **O que o processo significa**: C-002 (fluxo pedido → aprovação → registo/encomenda), C-005 (fórmula do valor do pedido).
- **Regras do negócio que não mudam**: M-1, M-2, M-3, M-4 — todas confirmadas em R-00/R-01, nenhuma correcção por evidência esta passagem.
- **Restrições estruturais**: C-004 (a verdade dos preços vive hoje no ERP-X — condição confirmada que gate a arquitectura de dados de qualquer opção); U-004 (ler em tempo real do ERP-X ou manter cópia própria — ainda em aberto, `swing: dimensionante`, muda o modelo de dados e o plano de integração, não elimina classes inteiras de solução).
- **Perguntas que mudam o caminho (decisivas)**: (none) — nenhuma `Unknown` aberta na SU carrega `swing: decisivo`; as duas mais estruturais (U-004, integração de dados) e U-006 (mecanismo de auditoria) são `dimensionante` — mudam desenho e esforço, não eliminam nem trocam a classe de solução viável.
- **Obrigações de âmbito e tarefas**: proponho nova linha (sem id ainda — a escrever pela síntese): o âmbito autorizado é pedido + aprovação + passagem a compras; gestão de stock e recepção física ficam fora — declarado pelo dono (pedido.md ¶4, locator persistido em `_capture/pedido.md.text.md`), com base machine-resolvable (declaração datada do dono, `Confirmed threshold`). U-006 (mecanismo de auditoria por desenhar, obrigação de M-3) também é uma obrigação de âmbito material.

### Open questions / Unknowns flagged

- U-001 — frequência do processo (pedidos por dia/semana/mês) — `quem responde: role: responsável de compras` — `criticidade: Low`.
- U-002 — contexto de uso do pedido (secretária, terreno, dispositivo, ligação) — `quem responde: role: requerente` — `criticidade: Med`.
- U-004 — ler preços em tempo real do ERP-X ou manter cópia própria — `quem responde: role: director de sistemas de informação` — `criticidade: Med`.
- U-006 — mecanismo de registo de quem aprovou o quê e quando — `quem responde: role: auditoria interna / role: director de sistemas de informação` — `criticidade: Med`.
- U-007 — envelope orçamental, modelo de financiamento e limiar de aprovação do projecto — `quem responde: role: direcção financeira / role: director de sistemas de informação` — `criticidade: Med`.
- U-008 — critério de sucesso do projecto — `quem responde: role: director de sistemas de informação` — `criticidade: Med`.
- U-009 — tempo por passo do processo hoje — `quem responde: role: responsável de compras / role: requerente` — `criticidade: Low`.
- U-010 — taxa horária carregada por passo — `quem responde: role: direcção financeira` — `criticidade: Low`.

### Conflicts seen

- X-001 — o caminho de urgência salta a aprovação prévia da chefia; não está declarado se também salta a aprovação da direcção financeira acima do limiar — `partes: operations∧governance` — `criticidade: Critical`. Sem resposta do dono (declarou não ter essa informação — council-log.md, R-02) e sem evidência interna do engagement que resolva o conflito em qualquer direcção (confirmado após duas passagens de Discovery e revisão independente). Fase avançou por `/frame --override`; X-001 mantém-se Conflicted e visível — fecha antes de qualquer entrega final que dependa dele.

### Risks

- R-001 — pedidos duplicados por reenvio, sem mecanismo de detecção hoje — `impacto: desperdício financeiro e rework em compras` — `mitigação: detectar duplicados por regra (mesmo requerente + conteúdo semelhante + janela curta); confirmação visível ao requerente (A-002)`.
- R-002 — cópia do catálogo de preços actualizada à mão, sem cadência definida — `impacto: encomendas com preços errados; divergências financeiras` — `mitigação: decidir fonte única de verdade para preços entre ERP-X e o novo sistema (U-004)`.
