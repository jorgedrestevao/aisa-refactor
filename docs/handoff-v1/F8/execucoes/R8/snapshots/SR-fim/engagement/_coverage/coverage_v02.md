# Revisão de cobertura — f8-r3-fx02 · etapa lens

> Projecção determinística do registo em JSON. **Não é autoridade**: os veredictos são recalculados a cada leitura e editar este ficheiro não muda nenhum deles.

| | |
|---|---|
| registo | `_coverage/coverage_v02.json` |
| produzido em | 2026-09-24T16:05:00Z |
| alvo | — (cobertura por perspectiva, passagem R-02) |
| revisões anteriores | `coverage_v01.json` |

## Veredictos

| dimensão | resultado |
|---|---|
| contrato do registo | válido (valid) |
| actualidade da base | actual (current) |
| revisão das fontes | not_applicable (not_applicable) |
| leitura nos dois sentidos | concluída (completed) |
| cobertura | com lacunas (gaps) |
| passo a que isto serve | close_round |
| pode avançar | sim |

## Porquê

- Seis perspectivas examinadas e revistas por quem não as escreveu; lacunas à vista e encaminhadas (5).

## Perspectivas

| perspectiva | estado | prova | porquê | leitura independente |
|---|---|---|---|---|
| business | gap | `C-002`, `C-003`, `M-1`, `M-2`, `M-3`, `M-4`, `A-001`, `U-008` | outcome (pedido -> aprovacao -> compra), regras (M-1..M-4) e excepcao urgente (C-003) declarados e evidenciados; impacto ainda qualitativo (A-001); criterio de sucesso nao declarado pelo dono (enquadramento.md#T4: "nao sei dizer") -- rota para U-008. | treated |
| operations | assessed | `C-002`, `C-003`, `R-001`, `U-001`, `U-009` | fluxo, responsabilidades e excepcao urgente evidenciados (C-002, C-003); falha operacional concreta registada (R-001); volume (U-001) e tempo por passo (U-009, P-5) por apurar, sem bloquear a resposta a quem corre/recupera o processo. | treated |
| user | gap | `U-002`, `A-002` | actores e tarefa evidenciados (matriz-papeis.md); contexto de uso real nao esta declarado -- rota para U-002; friccao de confirmacao de recepcao registada (A-002). | treated |
| data | gap | `C-004`, `C-005`, `C-007`, `A-003`, `R-002`, `U-004`, `M-4` | modelo, dono e risco de desactualizacao descritos e evidenciados (C-004, A-003, R-002); a formula de calculo esta confirmada (C-005). O mecanismo que garante consistencia do valor -- o ponto de arredondamento -- ja esta resolvido: so no total, ao centimo, meio-para-cima, declarado pelo responsavel de compras (C-007, was U-003, answers.md#U-003). A unica questao estrutural genuinamente em aberto nesta perspectiva e U-004 (ler precos em tempo real do ERP-X ou manter copia propria). | treated |
| governance | gap | `M-1`, `M-2`, `M-3`, `C-006`, `U-006`, `X-001` | separacao de papeis e obrigacao de auditoria declaradas (M-1..M-3). O valor do limiar de aprovacao financeira ja esta resolvido: 5000 EUR por pedido, declarado pela direccao financeira (C-006, was U-005, answers.md#U-005). As questoes genuinamente em aberto sao o mecanismo de auditoria por desenhar (U-006) e o conflito entre a via de urgencia e a aprovacao financeira por resolver (X-001, Conflicted, Critical). | treated |
| financial | gap | `A-004`, `A-005`, `U-001`, `U-007`, `U-009`, `U-010` | custo do nao-fazer-nada descrito qualitativamente (A-004); envelope de custo as-is ESCRITO como Assumed (A-005: formula custo = volume x tempo por passo x taxa carregada + duplicados + arredondamento), como o checklist manda mesmo sem numeros do cliente. Quantificacao bloqueada por tres factores em aberto: volume (U-001), tempo por passo (U-009) e taxa horaria carregada (U-010). Envelope orcamental do projecto (U-007) e uma questao distinta (tecto de investimento, nao custo as-is). | treated |

Conflitos entre fontes: `X-001`

## Lacunas conhecidas

| item | requisito | estado | o que falta | a quem toca |
|---|---|---|---|---|
| LENS:business | U-008 | gap | responder às perguntas abertas (U-008) | dono do processo |
| LENS:user | U-002 | gap | responder às perguntas abertas (U-002) | dono do processo |
| LENS:data | R-002, U-004 | gap | responder às perguntas abertas (R-002, U-004) | dono do processo |
| LENS:governance | U-006, X-001 | gap | responder às perguntas abertas (U-006, X-001) | dono do processo |
| LENS:financial | U-001, U-007, U-009, U-010 | gap | responder às perguntas abertas (U-001, U-007, U-009, U-010) | dono do processo |

## Fontes que não se conseguem ler

- `inputs/entrevista-processo.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/matriz-papeis.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/nota-dados.md` — sem extractor para .md (COV-CAPTURE-LIMIT)
- `inputs/pedido.md` — sem extractor para .md (COV-CAPTURE-LIMIT)

## Achados

| código | gravidade | onde | o que é | o que o fecha |
|---|---|---|---|---|
| `COV-KNOWN-GAP` | error | LENS:business | perspectiva `business` com lacuna encaminhada (U-008) | — |
| `COV-KNOWN-GAP` | error | LENS:user | perspectiva `user` com lacuna encaminhada (U-002) | — |
| `COV-KNOWN-GAP` | error | LENS:data | perspectiva `data` com lacuna encaminhada (R-002, U-004) | — |
| `COV-KNOWN-GAP` | error | LENS:governance | perspectiva `governance` com lacuna encaminhada (U-006, X-001) | — |
| `COV-KNOWN-GAP` | error | LENS:financial | perspectiva `financial` com lacuna encaminhada (U-001, U-007, U-009, U-010) | — |

## Quem reviu

- lens-coverage-reviewer (agent), read lens_coverage.dimensions and conflict_scan against shared-understanding.md (Confirmed/Assumed/Unknown/Conflicted/Risky rows), answers.md#U-003/#U-005, context.json, inputs/matriz-papeis.md, checked each ref against library/kernel/lens-checklists.md's central question and Coverage evidence per perspective, with focus on whether the data/governance corrections (U-003->C-007, U-005->C-006) hold and whether any ref still cites a resolved row as open
- limite declarado: user.justification names matriz-papeis.md as evidence for actors/task but that filename is not itself in user.refs (only U-002, A-002 are) -- a citation looseness, not a routing error, since the gap status already routes the missing piece (context of use) to U-002 correctly.
- limite declarado: 1a passagem (2026-09-24T15:00:00Z) tinha marcado data e governance `not_treated`: ambas citavam U-003 e U-005 como perguntas em aberto quando ja tinham sido resolvidas em R-01 (U-003 -> C-007, U-005 -> C-006, via /answer). Corrigido antes desta 2a passagem: refs e justification actualizados para citar C-007 e C-006, deixando aberto so o que genuinamente falta (data: U-004; governance: U-006, X-001). Esta 2a passagem confirma a correcção e re-verifica os seis.

---

Estrutura, cobertura, aprovação e ponta-a-ponta são quatro perguntas separadas, de propósito. Esta página responde à segunda.
