# Chairman Synthesis — Round O-02 / Phase Options (reabertura change-impact)

## Personas heard

- `solution-architect` (autor técnico, inline) — candidato único publicado, `_design/candidates.json` rev.2 (O-006).
- `specialist-reviewer` × 5, um por mandato, sobre a revisão 2: `architecture-review` (REV-0006), `data-integration` (REV-0007), `security-operation` (REV-0008), `ux-process` (REV-0009), `cost-estimate` (REV-0011 — substitui REV-0010, void por defeito de citação do executor). Os 5 relançados por relay (REV-0012..0016, mesmo conteúdo, versão literal/completa) não puderam ser publicados como pareceres formais — `STALE_INPUT` em `shared-understanding.md`, porque a síntese já tinha corrido sobre o conteúdo condensado antes de a versão literal chegar (ver `council-log.md#O-02`, nota de correcção de relay). Ficam `mandated` sem parecer; as versões literais completas estão guardadas em `lens-outputs/_council-prep/O-02-REV-0012.json`..`O-02-REV-0016.json` para auditoria — conferidas contra o que segue: mesma substância, sem achado que mude uma disposição já registada.

## Overlaps → strengthened

- "C-006 (limiar 5 000€) e C-007 (arredondamento meio-para-cima, total) continuam Confirmed sem linha sucessora, apesar de `mudancas.md` os superar" — achado independente de **4 dos 5** revisores (REV-0006.F04, REV-0008.F03, REV-0009.F01, REV-0011.F03) → **A-007** (was C-006), **A-008** (was C-007), ambas Assumed (documento do cliente sem papel nomeado, mesmo padrão de A-006 — não Confirmed).
- "TW-4 (decisions.md#D-002) cita o limiar por número literal (5 000€), já falso e dentro da própria zona crítica de X-001" — achado independente de **4 dos 5** revisores (REV-0006.F05, REV-0007.F05, REV-0008.F02, REV-0009.F02) → não é uma linha da SU (TW-4 vive em `decisions.md`, autoridade do dono) — carregado como acção delegada ao dono (ver *Achados dispostos*), nomeado em `options.md`.
- "O mecanismo que torna síncrono o recálculo de Pedido.valor_total / a semântica de arredondamento meio-para-par não está confirmado por nenhuma fonte do pacote" — achado independente de **2** revisores (REV-0006.F03, REV-0007.F01+F02) → **U-015** (Critical, proof_obligation).

## Gaps → carried as Assumed/Unknown

- "O ecrã de pedido pode precisar de aviso pré-submissão quando o valor cruza o novo limiar" — proposto só por `ux-process` (REV-0009.F05) → **U-016** (design_choice, Low).

## Contradictions → Conflicted

- Nenhuma. `review.py show-reviews` → `divergences: []`; os achados dos 5 pareceres convergem (reforçam-se), não discordam entre si.

## Admissão de perguntas

- **U-015** — proposta por `architecture-review` (REV-0006.F03) e `data-integration` (REV-0007.F01, F02) — admitida. Tipo: `proof_obligation`. Aspectos que move: `funcional`, `aceitacao`, `viabilidade` (se o mecanismo for assíncrono, a aprovação financeira M-2 pode nunca disparar correctamente — falha silenciosa de controlo). Campos preenchidos a partir dos dois pareceres; nenhum campo ficou vazio.
- **U-016** — proposta por `ux-process` (REV-0009.F05) — admitida. Tipo: `design_choice`, 2 alternativas reais (aviso pré-submissão / sem aviso). Aspecto que move: `funcional`. Baixa criticidade — não bloqueia nada, decide-se num `/answer`.
- **Não escritas** (sem aspecto que mova, ou requisito não pergunta):
  - REV-0006.F01 / REV-0011 (recomendações "coordenador: alargar knowledge_refs/input_refs do mandato") — processo de revisão desta reabertura, não facto do engagement; não escrito como linha SU.
  - REV-0007.F03 (sequenciar mecanismo de R-003 antes de custar o delta) — sequenciamento de trabalho, não pergunta ao dono; carregado como nota de risco (ver *Risks captured*).
  - REV-0007.F04 (confirmar com a contabilidade) e REV-0009.F06 (confirmar mitigação de R-003) — acções de verificação para `/blueprint`/`/synthesize`, não questões novas com alternativas reais; carregadas como recomendações em `options.md`.
  - REV-0007.F06 (frame.md retrato congelado) — nota de frescura de artefacto derivado, não um facto do engagement.
  - REV-0008.F01 (X-001 mais exposto) e REV-0008.F04 / REV-0009.F03 (obrigação de auditoria do limiar em vigor, estado observável do TW-4) — a organização já tem a pergunta certa aberta (X-001) e a decisão certa registada (TW-4); o que falta é trabalho de `/blueprint --refresh` (nomear o campo, o estado), não uma nova pergunta ao dono — **requisito, não pergunta pendente** (P-21/regra do CLAUDE.md).
  - REV-0009.F04 (critério de aceitação de fronteira do arredondamento) — condicional ao fecho técnico de U-015; sem base própria antes disso.

## Risks captured

- Nenhum risco novo (Risky) escrito nesta ronda. R-003/R-004 (já existentes) permanecem a base do risco de mecanismo de duplicados/cópia; a nota de sequenciamento (REV-0007.F03) e a de confirmação com a contabilidade (REV-0007.F04) ficam como recomendações associadas a R-003/C-007 em `options.md`, não como novas linhas Risky — não há impacto+mitigação adicional que R-003 já não carregue.

## SU rows written this round

- **A-007** — was C-006: limiar desce a 3 000€ (mudancas.md ¶3 [X3]).
- **A-008** — was C-007: arredondamento passa a linha-a-linha, meio-para-par (mudancas.md ¶1 [X1]).
- **U-015** — mecanismo síncrono de valor_total / arredondamento (proof_obligation, Critical, spike).
- **U-016** — aviso pré-submissão do limiar (design_choice, Low, reuniao).
- C-006 e C-007 marcadas `resolved -> A-007` / `resolved -> A-008` (sanctioned edit, última coluna).

## Phase artefact written

- `options.md` (overwrite) — um candidato (O-006), verdict `viable with preconditions`, terminal `conditionally preferred`; O-001..O-005 retirados (`retired_ids`) e listados em *Out of play*; 11 achados `deferred` nomeados em bloco próprio, com o `chairman-synthesis-O-02.md` (este ficheiro) como registo completo.

## Class coverage — round O-02

- `DO-NOTHING` — N/A esta ronda: nenhum candidato novo gerado (rota é o delta sobre D-002, não uma geração de classes) — ver O-005 (O-01, retirado, não reavaliado por esta mudança).
- `PROCESS-CHANGE` — N/A esta ronda, mesma razão — ver O-004 (O-01, retirado, não reavaliado).

## Concern coverage — round O-02

- C1 (justificação de intervenção) — não material: já assente em D-002, não reaberto.
- C2 (forma/propriedade) — não material: forma inalterada (model-driven/Dataverse).
- C3 (absolutos/viabilidade dura) — tocado: nenhum absoluto novo violado pelo delta.
- C4 (âmbito/propriedade dos dados) — não material: entidades inalteradas.
- C5 (criticidade/classe de trabalho) — não material: classe inalterada.
- C6 (catálogo de regras de cálculo) — **tocado a fundo**: eixo 6, ver U-015; regra conhecida, mecanismo por confirmar.
- C7 (operar/suportar) — tocado: obrigação de auditoria do limiar em vigor (REV-0008.F04), carregada para `/blueprint --refresh`.
- C8 (não usado nesta versão do pacote além dos 12 formais — sem nota própria).
- C9 (não usado — sem nota própria).
- C10 (segurança/segregação) — tocado: X-001 mais exposto com o limiar mais baixo (REV-0008.F01); sem mudança de estado da linha.
- C11 (economia/10 dimensões) — tocado: banda de esforço do delta revista (REV-0011.F01, aritmética reconciliada 0.25–3.6 dias).
- C12 (proof requirement) — tocado: teste empírico em sandbox Dataverse nomeado (U-015).

## Per-option long form

### O-006 — Pedido, aprovação e encomenda — model-driven, revisto (delta pós-aprovação)   ·   esta plataforma, mesma forma de O-002   ·   Power Apps (model-driven) + Dataverse + Power Automate
- **Anchored by**: solution-architect (candidato); architecture-review, data-integration, security-operation, ux-process, cost-estimate (pareceres, revisão 2).
- **Scope**: whole solution — herda O-002 por inteiro; scope: `_design/candidates.json#O-006`.
- **Viability**: viable with preconditions.
- **Outcome**: manter D-002 (adoptar O-002), absorvendo o delta [X1]/[X3] como mudança de regra de cálculo e de valor de configuração — não uma nova escolha de forma.
- **High-level architecture**: LinhaPedido.valor_linha (dentro — arredondamento próprio, mecanismo por confirmar), Pedido.valor_total (dentro — soma de linhas já arredondadas, mecanismo de recálculo por confirmar), Pedido.estado (dentro — mecânica inalterada, valor de C-006 muda), RegistoAprovacao (dentro — obrigação de gravar o limiar em vigor, por nomear). Nenhum componente fora da fronteira Power Platform.
- **Assumptions**: A-007 (limiar 3 000€), A-008 (arredondamento linha-a-linha/meio-para-par) — ambas Assumed, não Confirmed (documento sem papel nomeado).
- **Order of magnitude**: 30–38 dias (base O-002, inalterada) + 0.25–3.6 dias de delta · `PACK MODEL` (estimation-model.md; aritmética reconciliada por REV-0011.F01 — golden rule, arredondar para cima). Custo de mudar o valor do limiar: por confirmar se é referenciado (config, custo ~0) ou literal nalgum ponto do fluxo (custo pequeno de edição+teste de fronteira) — REV-0011.F03.
- **Material strengths**: nenhuma entidade, ecrã ou integração nova; Pedido.estado já lê o limiar por referência a C-006, não por número literal — só o TW-4 (decisions.md) quebra essa disciplina.
- **Disqualifiers**: (none).
- **Preconditions**: mecanismo de arredondamento/recálculo síncrono confirmado — fonte: teste técnico em sandbox Dataverse — não financiado — antes de `/blueprint --refresh` (U-015). Emenda de TW-4/decisions.md#D-002 (referenciar C-006/A-007 por id) — role: director de sistemas de informação — por fazer.
- **Material trade-offs**: nenhum novo — os de O-002 mantêm-se (mobile forfeit, U-002 em aberto).
- **Material risks**: A-008 sem confirmação da contabilidade (REV-0007.F04); X-001 mais exposto com o limiar mais baixo (REV-0008.F01).
- **Cost drivers**: C6 (regras de cálculo) e C10 (segregação/auditoria) — ambos tocados pelo delta; C11 revisto.
- **Reversibility**: alta para o delta (regra/config); inalterada da forma para o resto (alta entre formas Dataverse, baixa para sair da plataforma).
- **Revision condition**: se o mecanismo de arredondamento (U-015) resolver para plug-in síncrono em vez de coluna calculada, revê-se o custo e a arquitectura de baixo nível — nunca a forma.
- **Decision-changing uncertainties**: U-015 (Critical) — muda custo/arquitectura de baixo nível, nunca a escolha de O-002; fecho: teste empírico em sandbox Dataverse.
- **Proof requirement**: engineered test harness (sandbox Dataverse, valores 2.005/2.015/2.025€) — funded? não.
- **Concern notes**: eixo 6 (C6) é o único eixo técnico tocado; não muda o veredicto de viabilidade — fica requisito/risco do caminho já escolhido (decision-tree.md §6.1).

## Achados dispostos (24, `review.py dispose`)

Ver `_design/reviews/ledger.json` para o registo completo, imutável. Resumo por disposição:

- **`accepted`** (5) — REV-0006.F04 (→A-007,A-008), REV-0008.F03 (→A-007), REV-0009.F01 (→A-007), REV-0011.F03 (→A-007 + locator do blueprint).
- **`delegated`** (8) — REV-0006.F01 (reemitir mandato), REV-0006.F05/REV-0007.F05/REV-0008.F02/REV-0009.F02 (emendar TW-4), REV-0008.F04 (obrigação de auditoria), REV-0009.F03 (estado observável do TW-4), REV-0011.F01/F02 (aritmética e custos em falta — 2 findings, mesma disposição).
- **`deferred`** (11) — REV-0006.F02/F03, REV-0007.F01/F02/F03/F04/F06, REV-0008.F01, REV-0009.F04/F05/F06 — impacto registado, nomeados em `options.md` bloco *Achados por fechar*.

## Parser warnings

- Nenhum. Os 5 pareceres formais (REV-0006/0007/0008/0009/0011) validaram integralmente contra `handoff-review/1`.
- Nota de processo (não um parser warning, mas registada aqui por transparência): 3 dos 5 mandatos desta ronda (REV-0006 architecture-review, REV-0008 security-operation, REV-0009 ux-process, REV-0011 cost-estimate) foram publicados com `input_refs` por omissão (candidates.json, SU, frame.md, decisions.md) sem `_blueprint/ux-blueprint_v01.yaml` nem `options.md` — os próprios revisores nomearam isto como lacuna (REV-0006 `unanswered`, REV-0011 `recommended_actions`). Registado como acção delegada (ver *Achados dispostos*); não repetido nesta síntese por proporcionalidade com o âmbito da reabertura (change-impact, não nova descoberta).
