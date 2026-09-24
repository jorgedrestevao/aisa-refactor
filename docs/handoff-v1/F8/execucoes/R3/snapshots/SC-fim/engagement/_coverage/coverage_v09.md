# Revisão de cobertura — f8-r3-fx02 · etapa blueprint

> Projecção determinística do registo em JSON. **Não é autoridade**: os veredictos são recalculados a cada leitura e editar este ficheiro não muda nenhum deles.

| | |
|---|---|
| registo | `_coverage/coverage_v09.json` |
| produzido em | 2026-09-24T13:30:10Z |
| alvo | `_blueprint/ux-blueprint_v01.yaml` (v01) |
| revisões anteriores | `coverage_v04.json` |

## Veredictos

| dimensão | resultado |
|---|---|
| contrato do registo | válido (valid) |
| actualidade da base | actual (current) |
| revisão das fontes | completa (complete) |
| leitura nos dois sentidos | concluída (completed) |
| cobertura | com lacunas (gaps) |
| passo a que isto serve | approve_blueprint |
| pode avançar | não |

## Porquê

- Há obrigações por cobrir ou por fundamentar; a versão pode continuar em discussão, mas não se anuncia pronta para aprovação.

## Obrigações

| item | requisito | tratamento | estado | destinos |
|---|---|---|---|---|
| b-cov-001 | C-001 | preserve | covered | 1 |
| b-cov-002 | M-1, M-2, M-3, M-4 | preserve | covered | 2 |
| b-cov-003 | C-002, C-003 | preserve | covered | 1 |
| b-cov-004 | C-004, C-005, C-006, C-007 | preserve | covered | 2 |
| b-cov-005 | C-008 | preserve | covered | 1 |
| b-cov-006 | D-002 | preserve | covered | 1 |
| b-cov-007 | A-001, A-002, A-003, A-004, A-005 | preserve | partial | 1 |
| b-cov-008 | U-001 | preserve | excluded | 0 |
| b-cov-009 | U-009 | preserve | excluded | 0 |
| b-cov-010 | U-010 | preserve | excluded | 0 |
| b-cov-011 | U-002 | clarify | partial | 0 |
| b-cov-012 | U-013 | clarify | partial | 0 |
| b-cov-013 | U-004 | clarify | partial | 1 |
| b-cov-014 | U-012 | clarify | partial | 1 |
| b-cov-015 | U-006, M-3 | preserve | covered | 1 |
| b-cov-016 | U-007 | preserve | excluded | 0 |
| b-cov-017 | U-008 | preserve | excluded | 0 |
| b-cov-018 | U-011 | clarify | partial | 1 |
| b-cov-019 | X-001 | preserve | excluded | 0 |
| b-cov-020 | R-003, R-004 | preserve | partial | 1 |
| b-cov-021 | U-003 | preserve | covered | 1 |
| b-cov-022 | U-005 | preserve | covered | 1 |
| b-cov-023 | R-001, R-002 | preserve | excluded | 0 |
| b-cov-024 | D-001 | preserve | covered | 1 |

## Lacunas conhecidas

| item | requisito | estado | o que falta | a quem toca |
|---|---|---|---|---|
| b-cov-007 | A-001, A-002, A-003, A-004, A-005 | partial | None | None |
| b-cov-011 | U-002 | partial | levantamento junto de uma amostra de requerentes | role: requerente / role: director de sistemas de informação |
| b-cov-012 | U-013 | partial | confirmar instalabilidade/entitlement da app nativa, condicional ao fecho de U-002 | role: director de sistemas de informação |
| b-cov-013 | U-004 | partial | decisão do director de SI sobre a fonte de verdade dos preços, informada por U-012 | role: director de sistemas de informação |
| b-cov-014 | U-012 | partial | confirmação técnica de que a interface existe, quem a detém e que garantia documenta | role: director de sistemas de informação / fonte: ERP-X |
| b-cov-018 | U-011 | partial | verificação VC-05 e resposta do director de SI sobre licenciamento | role: director de sistemas de informação |
| b-cov-020 | R-003, R-004 | partial | se U-004 resolver para cópia local, nomear dono de reconciliação, cadência e deteção de drift | role: director de sistemas de informação |

## Fontes que não se conseguem ler

- `inputs/entrevista-processo.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/matriz-papeis.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/nota-dados.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/pedido.md` — sem extractor para .md (COV-CAPTURE-LIMIT)

## Achados

| código | gravidade | onde | o que é | o que o fecha |
|---|---|---|---|---|
| `COV-KNOWN-GAP` | warn | b-cov-007 | lacuna declarada (partial) sobre A-001, A-002, A-003, A-004, A-005 | None |
| `COV-KNOWN-GAP` | warn | b-cov-011 | lacuna declarada (partial) sobre U-002 | levantamento junto de uma amostra de requerentes |
| `COV-KNOWN-GAP` | warn | b-cov-012 | lacuna declarada (partial) sobre U-013 | confirmar instalabilidade/entitlement da app nativa, condicional ao fecho de U-002 |
| `COV-KNOWN-GAP` | warn | b-cov-013 | lacuna declarada (partial) sobre U-004 | decisão do director de SI sobre a fonte de verdade dos preços, informada por U-012 |
| `COV-KNOWN-GAP` | warn | b-cov-014 | lacuna declarada (partial) sobre U-012 | confirmação técnica de que a interface existe, quem a detém e que garantia documenta |
| `COV-KNOWN-GAP` | warn | b-cov-018 | lacuna declarada (partial) sobre U-011 | verificação VC-05 e resposta do director de SI sobre licenciamento |
| `COV-KNOWN-GAP` | warn | b-cov-020 | lacuna declarada (partial) sobre R-003, R-004 | se U-004 resolver para cópia local, nomear dono de reconciliação, cadência e deteção de drift |

## Quem reviu

- aisa (aisa-blueprint, passo 13b) (agent), leitura cruzada: fonte->desenho (cada obrigacao material da reconciliacao v04 contra um no concreto de ux-blueprint_v01.yaml) e desenho->fonte (cada campo/regra desenhada contra a SU/decisao que a justifica); nenhuma invencao de mecanismo sem su_ref.
- limite declarado: Sem workbook .xlsx no engagement — sem inventario L1/fields_draft.py; todos os campos desenhados carregam state=Assumed/Confirmed com source design/SU, nunca L1.

---

Estrutura, cobertura, aprovação e ponta-a-ponta são quatro perguntas separadas, de propósito. Esta página responde à segunda.
