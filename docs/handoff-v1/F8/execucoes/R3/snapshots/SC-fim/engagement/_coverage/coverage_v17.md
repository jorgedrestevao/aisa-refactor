# Revisão de cobertura — f8-r3-fx02 · etapa render

> Projecção determinística do registo em JSON. **Não é autoridade**: os veredictos são recalculados a cada leitura e editar este ficheiro não muda nenhum deles.

| | |
|---|---|
| registo | `_coverage/coverage_v17.json` |
| produzido em | 2026-09-24T14:15:00Z |
| alvo | `_render/f8-r3-fx02_executive-report_v01.md` (executive-report_v01) |
| revisões anteriores | `coverage_v13.json` |

## Veredictos

| dimensão | resultado |
|---|---|
| contrato do registo | válido (valid) |
| actualidade da base | actual (current) |
| revisão das fontes | completa (complete) |
| leitura nos dois sentidos | concluída (completed) |
| cobertura | com lacunas (gaps) |
| passo a que isto serve | complete_deliverable |
| pode avançar | não |

## Porquê

- Há 7 achado(s) impeditivo(s) por resolver (COV-DEAD-REF).

## Obrigações

| item | requisito | tratamento | estado | destinos |
|---|---|---|---|---|
| cov-001 | C-001 | preserve | covered | 1 |
| cov-002 | M-1, M-2, M-3, M-4 | preserve | covered | 1 |
| cov-005 | C-008 | preserve | covered | 1 |
| cov-006 | D-002 | preserve | covered | 2 |
| cov-007 | A-001, A-002, A-003, A-004, A-005 | clarify | partial | 3 |
| cov-008 | U-001 | preserve | covered | 1 |
| cov-009 | U-009 | preserve | covered | 1 |
| cov-010 | U-010 | preserve | covered | 1 |
| cov-011 | U-002 | preserve | covered | 2 |
| cov-012 | U-013 | preserve | covered | 2 |
| cov-013 | U-004 | preserve | covered | 1 |
| cov-014 | U-012 | preserve | covered | 1 |
| cov-015 | U-006, M-3 | preserve | covered | 2 |
| cov-016 | U-007 | preserve | covered | 1 |
| cov-017 | U-008 | preserve | covered | 1 |
| cov-018 | U-011 | preserve | covered | 1 |
| cov-019 | X-001 | preserve | covered | 1 |
| cov-020 | R-003, R-004 | preserve | covered | 1 |
| cov-022 | U-005 | preserve | covered | 1 |
| cov-024 | D-001 | preserve | covered | 1 |

## Lacunas conhecidas

| item | requisito | estado | o que falta | a quem toca |
|---|---|---|---|---|
| cov-007 | A-001, A-002, A-003, A-004, A-005 | partial | nenhuma acção pendente — facto de as-is, mantém-se no Discovery Report | aisa-render (altitude de decisão não reconstrói o as-is) |

## Fontes que não se conseguem ler

- `inputs/entrevista-processo.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/matriz-papeis.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/nota-dados.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/nota-urgentes.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/pedido.md` — sem extractor para .md (COV-CAPTURE-LIMIT)

## Achados

| código | gravidade | onde | o que é | o que o fecha |
|---|---|---|---|---|
| `COV-KNOWN-GAP` | warn | cov-007 | lacuna declarada (partial) sobre A-001, A-002, A-003, A-004, A-005 | nenhuma acção pendente — facto de as-is, mantém-se no Discovery Report |
| `COV-DEAD-REF` | error | sr-as-is-out-of-scope | `links.coverage_items` aponta para um item que não existe no registo: cov-003 | corrigir a ligação ou repor o item |
| `COV-DEAD-REF` | error | sr-as-is-out-of-scope | `links.coverage_items` aponta para um item que não existe no registo: cov-004 | corrigir a ligação ou repor o item |
| `COV-DEAD-REF` | error | sr-as-is-out-of-scope | `links.coverage_items` aponta para um item que não existe no registo: cov-021 | corrigir a ligação ou repor o item |
| `COV-DEAD-REF` | error | sr-as-is-out-of-scope | `links.coverage_items` aponta para um item que não existe no registo: cov-023 | corrigir a ligação ou repor o item |
| `COV-DEAD-REF` | error | sr-as-is-out-of-scope | `links.coverage_items` aponta para um item que não existe no registo: cov-025 | corrigir a ligação ou repor o item |
| `COV-DEAD-REF` | error | sr-as-is-out-of-scope | `links.coverage_items` aponta para um item que não existe no registo: cov-026 | corrigir a ligação ou repor o item |
| `COV-DEAD-REF` | error | sr-as-is-out-of-scope | `links.coverage_items` aponta para um item que não existe no registo: cov-027 | corrigir a ligação ou repor o item |

## Quem reviu

- aisa-render (segmento S4 F8) (agent), leitura do documento renderizado contra as obrigacoes herdadas do registo a montante; passagem fonte->destino (cada obrigacao, e onde aterrou) e destino->fonte (cada mecanismo material declarado, e de onde vem).

---

Estrutura, cobertura, aprovação e ponta-a-ponta são quatro perguntas separadas, de propósito. Esta página responde à segunda.
