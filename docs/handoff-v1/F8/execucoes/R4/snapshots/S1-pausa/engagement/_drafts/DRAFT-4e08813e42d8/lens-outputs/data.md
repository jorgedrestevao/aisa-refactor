## R-01 — data

**What matters**: a verdade do pedido de reembolso vive em três lugares sucessivos antes de estabilizar — a folha do colaborador, "outra folha" da contabilidade, e por fim o ERP-X (C-004) — sem que nenhuma fonte descreva a folha intermédia (dono, estrutura, retenção); isso é, por si, um risco de erro silencioso de transcrição (R-001). O ERP-X já tem uma interface de pagamentos a colaboradores, nunca usada para este fim (C-005) — capacidade existente, por explorar em Options, não um facto que decida nada agora. Falta saber onde vive a informação do colaborador que uma aprovação automática precisaria de consultar — chefia directa, centro de custo (U-006).

**Tensions / risks**: a folha intermédia sem dono nem validação é candidata a erro silencioso de transcrição, e já há indício indirecto (os duplicados e atrasos de C-002 nascem exactamente da falta de validação entre passos) — ver R-001.

**Open evidence**:
- `dados: folha intermédia da contabilidade, sem descrição` → ADOPT → R-001
- `estrutural: interface de pagamentos do ERP-X existe, por explorar em Options` → ADOPT → C-005
- `processo: folha intermédia pode ser acidente de integração, não requisito` → DISMISS — hipótese de complexidade acidental; a evidência já aponta para acidente de integração (nenhuma fonte dá razão de negócio para a folha intermédia) e a arquitectura decide-o em Options, sem pergunta ao dono aqui
