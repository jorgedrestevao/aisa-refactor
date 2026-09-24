# Revisão de cobertura — f8-r3-fx02 · etapa reconciliation

> Projecção determinística do registo em JSON. **Não é autoridade**: os veredictos são recalculados a cada leitura e editar este ficheiro não muda nenhum deles.

| | |
|---|---|
| registo | `_coverage/coverage_v04.json` |
| produzido em | 2026-09-24T13:12:53Z |
| alvo | — (reconciliação) |
| revisões anteriores | — |

## Veredictos

| dimensão | resultado |
|---|---|
| contrato do registo | válido (valid) |
| actualidade da base | actual (current) |
| revisão das fontes | completa (complete) |
| leitura nos dois sentidos | concluída (completed) |
| cobertura | com lacunas (gaps) |
| passo a que isto serve | produce_blueprint |
| pode avançar | sim |

## Porquê

- Pode avançar-se para o desenho com as lacunas à vista e encaminhadas (13).

## Obrigações

| item | requisito | tratamento | estado | destinos |
|---|---|---|---|---|
| cov-001 | C-001 | preserve | covered | 0 |
| cov-002 | M-1, M-2, M-3, M-4 | preserve | covered | 0 |
| cov-003 | C-002, C-003 | preserve | covered | 0 |
| cov-004 | C-004, C-005, C-006, C-007 | preserve | covered | 0 |
| cov-005 | C-008 | preserve | covered | 0 |
| cov-006 | D-002 | preserve | covered | 0 |
| cov-007 | A-001, A-002, A-003, A-004, A-005 | preserve | covered | 0 |
| cov-008 | U-001 | clarify | partial | 0 |
| cov-009 | U-009 | clarify | partial | 0 |
| cov-010 | U-010 | clarify | partial | 0 |
| cov-011 | U-002 | clarify | partial | 0 |
| cov-012 | U-013 | clarify | partial | 0 |
| cov-013 | U-004 | clarify | partial | 0 |
| cov-014 | U-012 | clarify | partial | 0 |
| cov-015 | U-006, M-3 | clarify | partial | 0 |
| cov-016 | U-007 | clarify | partial | 0 |
| cov-017 | U-008 | clarify | partial | 0 |
| cov-018 | U-011 | clarify | partial | 0 |
| cov-019 | X-001 | clarify | partial | 0 |
| cov-020 | R-003, R-004 | preserve | covered | 0 |
| cov-021 | U-003 | preserve | covered | 0 |
| cov-022 | U-005 | preserve | covered | 0 |
| cov-023 | R-001, R-002 | clarify | partial | 0 |
| cov-024 | D-001 | preserve | covered | 0 |

## Lacunas conhecidas

| item | requisito | estado | o que falta | a quem toca |
|---|---|---|---|---|
| cov-008 | U-001 | partial | resposta do responsável de compras sobre volume mensal/semanal | role: responsável de compras |
| cov-009 | U-009 | partial | resposta de quem faz cada passo hoje, por passo | role: responsável de compras / role: requerente |
| cov-010 | U-010 | partial | resposta da direcção financeira/RH sobre a taxa carregada | role: direcção financeira |
| cov-011 | U-002 | partial | levantamento junto de uma amostra de requerentes | role: requerente / role: director de sistemas de informação |
| cov-012 | U-013 | partial | confirmar instalabilidade/entitlement da app nativa nos dispositivos dos requerentes, condicional ao fecho de U-002 | role: director de sistemas de informação |
| cov-013 | U-004 | partial | decisão do director de SI sobre a fonte de verdade dos preços, informada por U-012 | role: director de sistemas de informação |
| cov-014 | U-012 | partial | confirmação técnica de que a interface existe, quem a detém e que garantia documenta | role: director de sistemas de informação / fonte: ERP-X |
| cov-015 | U-006, M-3 | partial | decisão de desenho do mecanismo de auditoria neste blueprint | role: director de sistemas de informação / role: auditoria interna |
| cov-016 | U-007 | partial | resposta da direcção financeira/director de SI sobre orçamento | role: direcção financeira / role: director de sistemas de informação |
| cov-017 | U-008 | partial | decisão do dono sobre o critério de sucesso, em /decide ou /blueprint | role: director de sistemas de informação |
| cov-018 | U-011 | partial | verificação VC-05 (licensing-and-cost-drivers.md) e resposta do director de SI sobre licenciamento disponível/a adquirir | role: director de sistemas de informação |
| cov-019 | X-001 | partial | decisão do dono sobre a regra do caminho urgente face ao limiar financeiro (/answer X-001) | role: director de sistemas de informação |
| cov-023 | R-001, R-002 | partial | confirmar com o mantenedor do motor/skill porque R-001/R-002 não transitam para resolved=true quando R-003/R-004 as citam como "was"; corrigir a escrita se for defeito, não reinterpretar por leitura | aisa (mantenedor do motor/skill, fora do papel do dono do processo) |

## Fontes que não se conseguem ler

- `inputs/entrevista-processo.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/matriz-papeis.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/nota-dados.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/pedido.md` — sem extractor para .md (COV-CAPTURE-LIMIT)

## Achados

| código | gravidade | onde | o que é | o que o fecha |
|---|---|---|---|---|
| `COV-KNOWN-GAP` | warn | cov-008 | lacuna declarada (partial) sobre U-001 | resposta do responsável de compras sobre volume mensal/semanal |
| `COV-KNOWN-GAP` | warn | cov-009 | lacuna declarada (partial) sobre U-009 | resposta de quem faz cada passo hoje, por passo |
| `COV-KNOWN-GAP` | warn | cov-010 | lacuna declarada (partial) sobre U-010 | resposta da direcção financeira/RH sobre a taxa carregada |
| `COV-KNOWN-GAP` | warn | cov-011 | lacuna declarada (partial) sobre U-002 | levantamento junto de uma amostra de requerentes |
| `COV-KNOWN-GAP` | warn | cov-012 | lacuna declarada (partial) sobre U-013 | confirmar instalabilidade/entitlement da app nativa nos dispositivos dos requerentes, condicional ao fecho de U-002 |
| `COV-KNOWN-GAP` | warn | cov-013 | lacuna declarada (partial) sobre U-004 | decisão do director de SI sobre a fonte de verdade dos preços, informada por U-012 |
| `COV-KNOWN-GAP` | warn | cov-014 | lacuna declarada (partial) sobre U-012 | confirmação técnica de que a interface existe, quem a detém e que garantia documenta |
| `COV-KNOWN-GAP` | warn | cov-015 | lacuna declarada (partial) sobre U-006, M-3 | decisão de desenho do mecanismo de auditoria neste blueprint |
| `COV-KNOWN-GAP` | warn | cov-016 | lacuna declarada (partial) sobre U-007 | resposta da direcção financeira/director de SI sobre orçamento |
| `COV-KNOWN-GAP` | warn | cov-017 | lacuna declarada (partial) sobre U-008 | decisão do dono sobre o critério de sucesso, em /decide ou /blueprint |
| `COV-KNOWN-GAP` | warn | cov-018 | lacuna declarada (partial) sobre U-011 | verificação VC-05 (licensing-and-cost-drivers.md) e resposta do director de SI sobre licenciamento disponível/a adquirir |
| `COV-KNOWN-GAP` | warn | cov-019 | lacuna declarada (partial) sobre X-001 | decisão do dono sobre a regra do caminho urgente face ao limiar financeiro (/answer X-001) |
| `COV-KNOWN-GAP` | warn | cov-023 | lacuna declarada (partial) sobre R-001, R-002 | confirmar com o mantenedor do motor/skill porque R-001/R-002 não transitam para resolved=true quando R-003/R-004 as citam como "was"; corrigir a escrita se for defeito, não reinterpretar por leitura |

## Quem reviu

- aisa (aisa-blueprint, passo 1e — reconciliação) (agent), leitura de todas as unidades do inventario (coverage.py inventory) contra a Shared Understanding e decisions.md, cruzada com as disposicoes ja registadas em council-log.md (R-01, R-02, O-01) e com options.md/premortem.md para as condicoes e tripwires de D-002.
- limite declarado: 4 ficheiros de inputs/ sem extractor para .md (COV-CAPTURE-LIMIT) — tratados unverifiable, cobertos pelas extraccoes de texto correspondentes.

---

Estrutura, cobertura, aprovação e ponta-a-ponta são quatro perguntas separadas, de propósito. Esta página responde à segunda.
