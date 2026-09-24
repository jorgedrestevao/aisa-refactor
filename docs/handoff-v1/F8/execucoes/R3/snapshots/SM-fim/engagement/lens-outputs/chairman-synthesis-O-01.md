# Chairman Synthesis — Round O-01 / Phase Options

## Personas heard
- solution-architect (autor técnico, inline) — candidatos publicados (`_design/candidates.json` rev.1)
- architecture-review (REV-0001)
- data-integration (REV-0002)
- security-operation (REV-0003)
- ux-process (REV-0004)
- cost-estimate (REV-0005)

## Overlaps → strengthened
- "Entitlement/licenciamento das 5 populações para Power Apps/Dataverse não verificado" — anchored by architecture-review (REV-0001.F02) e cost-estimate (REV-0005.F02), independentemente → U-011 (Unknown; concordância entre dois revisores não é evidência — nenhuma linha Confirmed daqui, só a admissão da pergunta com base M-3/M-4).

## Gaps → carried as Assumed/Unknown
- "O ERP-X expõe interface programável para o catálogo de preços?" — proposto só por data-integration (REV-0002.F02) → U-012 (Unknown).
- "A app nativa do Power Apps está instalável/licenciada nos dispositivos dos requerentes, para O-002?" — proposto só por ux-process (REV-0004.F02) → U-013 (Unknown).

## Contradictions → Conflicted
- (nenhuma) — os cinco pareceres não se contradizem entre si; `review.py show-reviews` → `divergences: []`. Duas linhas (REV-0001.F02 / REV-0005.F02) convergem no mesmo achado por caminhos diferentes — tratado como reforço de uma única pergunta (U-011), não como divergência.

## Admissão de perguntas
- U-011 — "As 5 populações têm entitlement/licenciamento suficiente para Power Apps/Dataverse dado M-3/M-4?" — admitida — tipo: fact_gap — impacto: custo, viabilidade — por preencher: — (todos os campos preenchidos a partir de REV-0001.F02/REV-0005.F02, licensing-and-cost-drivers.md §5-6/§15).
- U-012 — "O ERP-X expõe interface programável para o catálogo?" — admitida — tipo: fact_gap — impacto: solucao, funcional — por preencher: — (marcador TO-BE DIVERGENCE usado no lugar de M-n, por não haver invariante de negócio que sirva directamente esta pergunta técnica).
- U-013 — "A app nativa está instalável/licenciada para O-002?" — admitida, condicional ao fecho de U-002 — tipo: fact_gap — impacto: componentes, esforço de alto nível — por preencher: — (marcador TO-BE DIVERGENCE, condicional).
- REV-0001.F01 (reversibilidade de O-003 incompleta) — não escrita como Unknown: é uma correcção de texto do candidato (achado sobre a arquitectura publicada), não uma pergunta ao dono — disposição `delegated` ao autor técnico.
- REV-0001.F03 / REV-0002.F04 (apresentação dispersa dos factores decisivos / da condição de fecho) — não escritas como Unknown: são recomendações de composição do artefacto, resolvidas neste mesmo round em `options.md` — disposição `accepted`.
- REV-0002.F01 / REV-0004.F01 (mecanismo de duplicados não idempotente + jornada de excepção sem critério) — não escritas como Unknown novo: correcção por evidência de um risco já existente (R-001) — viram R-003 (`was R-001`), disposição `accepted`.
- REV-0002.F03 (cópia local como anti-padrão de cache) — não escrita como Unknown novo: correcção por evidência de R-002 — vira R-004 (`was R-002`), disposição `accepted`.
- REV-0003.F01/F02/F04 (auditoria O-001/O-002 por concretizar, texto de O-002 sobre-estima o herdado, C-003 fora dos premise_refs) — não escritas como Unknown novo: a pergunta de mecanismo de auditoria já existe (U-006); as outras duas são correcções de texto do candidato — disposição `delegated` ao autor técnico.
- REV-0003.F03 (segregação do limiar em O-003 não imposta pela loja) — não escrita como Unknown: é um achado de viabilidade sobre um candidato específico (disqualifier/precondição), projectado directamente em `options.md#O-003` — disposição `accepted`.
- REV-0005.F01/F03 (multiplicador de complexidade não justificado; fluxo de sincronização da cópia local pode faltar na contagem) — não escritas como Unknown: são achados sobre a exactidão do número já publicado, a corrigir pelo autor na próxima revisão — disposição `delegated`.

## Risks captured
- R-003 (was R-001) — mecanismo de duplicados descrito não é idempotente/recuperável; jornada de excepção sem critério de aceitação.
- R-004 (was R-002) — cópia local do catálogo é cache de valor volátil sem reconciliação/cadência/deteção de drift obrigatórias.

## SU rows written this round
- U-011 — entitlement/licenciamento Power Platform para as 5 populações, face a M-3/M-4.
- U-012 — capacidade de integração do ERP-X (interface programável para o catálogo).
- U-013 — instalabilidade/entitlement da app nativa móvel, condicional a U-002, para o forfeit de O-002.
- R-003 (was R-001) — mitigação de duplicados corrigida por evidência (não idempotente como descrita).
- R-004 (was R-002) — cópia local do catálogo como anti-padrão de cache de valor volátil.

## Phase artefact written
- `options.md` — 5 candidatos (O-001..O-005), sem recomendação entre O-001/O-002 (swing: U-002), O-003 viável com pré-condições (segregação do limiar M-2), O-004/O-005 não endereçam M-3/R-001/R-002.

## Class coverage — round O-01
- `DO-NOTHING` — O-005
- `PROCESS-CHANGE` — O-004

## Concern coverage — round O-01
- C1 (Need, value, existing capability) — D2: exclusões documentadas (extensão do ERP-X, capacidade nativa da ferramenta de colaboração) e DO-NOTHING/PROCESS-CHANGE gerados (candidates.json#exclusions; O-004; O-005).
- C2 (Functional and process fit) — D1: regras de cálculo (C-005, C-007) e routing de aprovação (M-2/C-006) cobertos na arquitectura; gap — fluxo de urgência (C-003) fora dos premise_refs em O-001/O-002/O-003 (REV-0003.F04).
- C3 (User and experience fit) — D1: revisto por ux-process (REV-0004); gaps — U-002 (contexto/dispositivo), U-013 (entitlement móvel condicional), jornada de excepção sem critério (R-003).
- C4 (Data and information fit) — D1: revisto por data-integration (REV-0002); gaps — U-004 (fonte de verdade), U-012 (capacidade do ERP-X), R-004 (cópia local como cache).
- C5 (Integration and ecosystem fit) — D1: mesmo parecer (REV-0002) — leitura do ERP-X por connector directo assumida, sem confirmação de interface (U-012).
- C6 (Security, privacy and control) — D2: revisto por security-operation (REV-0003) — achado `blocking` em O-003 (segregação do limiar M-2 não imposta pela loja); U-006 (mecanismo de auditoria) ainda aberto para O-001/O-002.
- C7 (Governance, authority and compliance) — D1: mesmo parecer — X-001 (papel do dono no caminho de urgência) confirmado não pressuposto por nenhum candidato; fecha por decisão do dono, fora desta ronda.
- C8 (Lifecycle, ALM and change) — D0 — não material aqui: nenhum requisito de ciclo de vida/isolamento de ambiente além do padrão ALM do pacote foi levantado por nenhum revisor ou pela SU nesta ronda; nenhum papel de revisão foi accionado por sinal de ALM (`review.py route` não listou `governance-and-environments` como gatilho de ALM, só de auditoria).
- C9 (Scale, performance and resilience) — D0 — não material aqui, provisoriamente: natureza do processo (pedidos internos de equipamento) e ausência de sinal de volume elevado; a confirmar quando U-001 (frequência, Low) fechar.
- C10 (Operability, support and ownership) — D0 — não material aqui: nenhum requisito de suporte/operação além do padrão de um ambiente Power Platform gerido foi levantado nesta ronda.
- C11 (Economics, entitlement and TCO) — D2: revisto por cost-estimate (REV-0005) — achado material sobre o multiplicador de complexidade não justificado (REV-0005.F01) e sobre entitlement/licenciamento por verificar (REV-0005.F02 = REV-0001.F02 → U-011).
- C12 (Strategic fit, reversibility and dependency) — D2: revisto por architecture-review (REV-0001) — reversibilidade confirmada para O-001/O-002; incompleta para O-003 (custo de rebinding de ecrãs não nomeado, REV-0001.F01).

## Per-option long form

### O-001 — Pedido, aprovação e encomenda — app de ecrãs (canvas) sobre o Dataverse   ·   Esta plataforma — forma: app de ecrãs (canvas) sobre loja governada   ·   Power Apps (canvas) + Dataverse + Power Automate
- **Anchored by**: solution-architect; architecture-review; data-integration; security-operation; ux-process; cost-estimate
- **Scope**: whole solution
- **Viability**: viable with preconditions
- **Outcome**: intervenção tecnológica viável dentro da plataforma imposta (C-001), condicional ao fecho de U-006 (mecanismo de auditoria), U-011 (entitlement) e U-012 (capacidade do ERP-X)
- **High-level architecture**: tabelas Dataverse (Pedido, Linha de pedido, Registo de aprovação, Catálogo condicional), regras de negócio (cálculo C-005, arredondamento C-007, limiar M-2/C-006), fluxos (routing de aprovação, confirmação de recepção, detecção de duplicados — mecanismo por concretizar, ver R-003 —, leitura ERP-X), 4 ecrãs canvas, segurança por papel Dataverse — tudo dentro da fronteira C-001
- **Assumptions**: A-001 (impacto qualitativo), A-002 (confirmação de recepção necessária, ainda por validar com o requerente — REV-0004.F01)
- **Order of magnitude**: 40–50 dias (~8–10 semanas, 1 developer) · `PACK MODEL` (candidates.json#O-001 — multiplicador 1.2× não justificado pela contagem de entidades do próprio modelo do pacote — 4 tabelas cai na banda Simple/1.0×; REV-0005.F01 — banda a rever pelo autor antes de /decide; asimetria: modelo só calculado do lado da plataforma, sem equivalente para O-004/O-005)
- **Material strengths**: segurança e auditoria ao nível da coluna disponíveis na loja (Dataverse), base para satisfazer M-3/M-2 uma vez U-006 desenhado; sem forfeit de superfície documentado
- **Disqualifiers**: (none)
- **Preconditions**: mecanismo de auditoria concreto (imutabilidade + retenção alinhada a M-4) — arquitecto/director de SI — não financiado nomeadamente, dentro do orçamento do projecto — antes do blueprint (U-006); entitlement/licenciamento verificado (VC-05) — director de SI — antes de /decide (U-011); capacidade de integração do ERP-X confirmada — director de SI/ERP-X — antes de fechar U-004 (U-012)
- **Material trade-offs**: custo mais alto que O-002 pelo desenho manual dos 4 ecrãs canvas
- **Material risks**: R-003 (duplicados — mecanismo a concretizar); R-004 (cópia local do catálogo, se U-004 resolver assim); entitlement não verificado (U-011)
- **Cost drivers**: 4 ecrãs canvas complexos (maior driver); integração ERP-X; segurança por papel
- **Reversibility**: high — trocar para model-driven (O-002) é redesenho de ecrãs, dados/segurança ficam; low para sair da plataforma (fora de causa, C-001)
- **Revision condition**: U-002 confirma acesso predominantemente móvel/terreno sem necessidade dos ecrãs canvas desenhados — reabrir face a O-002/O-003
- **Decision-changing uncertainties**: U-002 (contexto de uso — swing entre O-001/O-002, sem custo de fecho adicional: levantamento junto de requerentes); U-006 (mecanismo de auditoria — custo: desenho em blueprint); U-011 (entitlement — custo: verificação VC-05)
- **Proof requirement**: bounded pilot (UAT da regra de duplicados corrigida, ver R-003)
- **Concern notes**: C6 decide a favor da loja Dataverse face a O-003 (segurança de coluna disponível); C11 ainda com número em revisão (REV-0005.F01)

### O-002 — Pedido, aprovação e encomenda — app orientada a registos (model-driven) sobre o Dataverse   ·   Esta plataforma — forma: app orientada a registos (model-driven) sobre loja governada   ·   Power Apps (model-driven) + Dataverse + Power Automate
- **Anchored by**: solution-architect; architecture-review; data-integration; security-operation; ux-process; cost-estimate
- **Scope**: whole solution
- **Viability**: viable with preconditions
- **Outcome**: intervenção tecnológica viável dentro da plataforma imposta (C-001), condicional ao mesmo trio de O-001 (U-006, U-011, U-012) mais o forfeit de acesso móvel (U-002/U-013)
- **High-level architecture**: mesmo modelo de dados e fluxos de O-001 (mesmas tabelas, mesmas regras, mesmo mecanismo de duplicados a concretizar — R-003); ecrãs gerados pela shell orientada a registos em vez de desenhados; captura de auditoria é a mesma configuração de tabela que O-001 — a vista de histórico é que vem gerada pela shell (correcção por evidência de REV-0003.F02 face ao texto original "herdada")
- **Assumptions**: A-001, A-002 (mesmas de O-001)
- **Order of magnitude**: 30–38 dias (~6–8 semanas, 1 developer) · `PACK MODEL` (candidates.json#O-002 — mesma ressalva de multiplicador que O-001, REV-0005.F01; asimetria: idem)
- **Material strengths**: ecrãs mais baratos (gerados pela shell); mesma base de segurança/auditoria de O-001 (Dataverse)
- **Disqualifiers**: (none) — o forfeit de móvel é uma precondição, não um desqualificador confirmado (depende de U-002/U-013, ambos ainda abertos)
- **Preconditions**: as três de O-001 (U-006, U-011, U-012); adicionalmente — confirmar que o acesso não é predominantemente móvel, ou que a app nativa é instalável/licenciada para os requerentes — director de SI — antes de /decide (U-002, U-013)
- **Material trade-offs**: browser de telemóvel não suportado pela shell orientada a registos (application-surfaces.md §3) — aceitável só se U-002/U-013 o permitirem
- **Material risks**: R-003; R-004 (se U-004→cópia local); entitlement não verificado (U-011); forfeit de móvel não resolvido (U-013)
- **Cost drivers**: integração ERP-X; segurança por papel; ecrãs (driver menor que O-001)
- **Reversibility**: high — trocar para canvas (O-001) é redesenho de ecrãs, dados ficam; low para sair da plataforma
- **Revision condition**: U-002 confirma necessidade de acesso móvel e U-013 não resolve a favor — reabrir face a O-001
- **Decision-changing uncertainties**: U-002 (swing entre O-001/O-002); U-013 (decide se o forfeit é aceitável, condicional a U-002); U-006; U-011
- **Proof requirement**: bounded pilot (mesma UAT de O-001)
- **Concern notes**: C3 é o que separa O-002 de O-001 — mesmo tudo o resto, o forfeit de móvel é a única diferença material por resolver

### O-003 — Pedido, aprovação e encomenda — app de ecrãs (canvas) sobre listas da ferramenta de colaboração   ·   Esta plataforma — forma: app de ecrãs (canvas) sobre listas da ferramenta de colaboração   ·   Power Apps (canvas) + listas + Power Automate
- **Anchored by**: solution-architect; architecture-review; data-integration; security-operation; ux-process; cost-estimate
- **Scope**: whole solution
- **Viability**: viable with preconditions
- **Outcome**: intervenção tecnológica viável dentro da plataforma imposta (C-001), condicional a uma precondição estrutural que O-001/O-002 não carregam: declaração formal de risco residual para o limiar financeiro (M-2), porque a loja não o pode impor
- **High-level architecture**: mesmas entidades e fluxos de O-001, guardados em listas em vez de tabelas Dataverse; regras de cálculo (C-005, C-007) absorvidas nos fluxos/canvas em vez de regras de negócio da loja; mesmo mecanismo de duplicados a concretizar (R-003)
- **Assumptions**: A-001, A-002
- **Order of magnitude**: 28–35 dias (~6–7 semanas, 1 developer) · `PACK MODEL` (candidates.json#O-003 — mesma ressalva de multiplicador, REV-0005.F01)
- **Material strengths**: custo mais baixo dos três (tabelas e ecrãs mais baratos sobre listas)
- **Disqualifiers**: segregação do limiar de 5 000 € (M-2/C-006) não imposta ao nível da loja — listas sem segurança de coluna; qualquer papel com direito de edição pode contornar sem detecção (evidência confirmada — security-controls.md §4/§7; REV-0003.F03, severidade `blocking`) — desqualificador provisório: só é aceitável com controlo compensatório e risco residual assinado por um dono
- **Preconditions**: declaração formal de risco residual (pack §13 — plano, respeito parcial, população fora do controlo, controlo compensatório, vector residual, data de reverificação) assinada por um dono — director de SI/auditoria interna — antes de /decide; as três de O-001 (U-006, U-011, U-012) igualmente aplicáveis; reversibilidade a corrigir com o custo de reapontar fontes de dados/fórmulas por ecrã (REV-0001.F01), não só migração de registos
- **Material trade-offs**: auditoria e controlo de acesso "mais fracos de origem" (texto do próprio candidato) face a Dataverse
- **Material risks**: R-003; R-004; risco de segregação do limiar (novo, decorrente de REV-0003.F03, sem linha SU própria — fica no candidato, corrigível pelo autor)
- **Cost drivers**: menor esforço de tabelas/ecrãs; sem componente de "regra de negócio" da Dataverse
- **Reversibility**: **incompleta como publicada** (candidates.json diz "média — migração de dados, não reconfiguração de ecrã"); architecture-review (REV-0001.F01) mostra que também exige reapontar fontes de dados e rever fórmulas por ecrã — correcção delegada ao autor, ainda não publicada
- **Revision condition**: declaração de risco residual recusada por um dono, ou controlo compensatório não disponível — reconsiderar O-003 face a O-001/O-002
- **Decision-changing uncertainties**: a mesma declaração de risco residual (acima) é o que decide se O-003 continua na mesa
- **Proof requirement**: bounded pilot; adicionalmente, prova do controlo compensatório do limiar (se a declaração de risco residual for o caminho escolhido)
- **Concern notes**: C6 é o que separa O-003 dos outros dois — única incapacidade estrutural da loja, não uma lacuna de informação

### O-004 — Mudar o processo — sem construir nada   ·   Mudar o processo; construir nada   ·   sem tecnologia — disciplina de processo
- **Anchored by**: solution-architect
- **Scope**: whole solution
- **Viability**: viable with preconditions
- **Outcome**: mudança de processo sem construção — não endereça de forma fiável a obrigação de auditoria (M-3); PROCESS-CHANGE desta ronda
- **High-level architecture**: numeração de pedidos, confirmação de recepção por resposta ao email, cadência de actualização do catálogo designada, procedimento escrito para arredondamento (C-007) e limiar (C-006) — sem componentes de plataforma
- **Assumptions**: A-004, A-005 (custo do processo actual, não quantificado)
- **Order of magnitude**: `ORDER OF MAGNITUDE UNAVAILABLE — o modelo do pacote só conta componentes de construção em plataforma; este candidato não constrói nada — o esforço é de gestão de mudança (redigir procedimento, formar quatro equipas), sem linha equivalente no modelo`
- **Material strengths**: reversível sem nada a desmontar; custo de implementação mínimo
- **Disqualifiers**: (none) — permanece viável como classe condicional, com a precondição abaixo
- **Preconditions**: aceitar o risco residual de M-3 (sem mecanismo de registo verificável além do email) ou desenhar um compensatório manual — director de SI/auditoria interna — antes de /decide
- **Material trade-offs**: depende de disciplina humana continuada (numerar, confirmar, actualizar); o mesmo tipo de falha que gerou R-003/R-004 fica sem barreira estrutural
- **Material risks**: R-003 (mitigação fraca — só disciplina humana); R-004 (idem); M-3 sem mecanismo fiável
- **Cost drivers**: (none) — gestão de mudança, não construção
- **Reversibility**: high
- **Revision condition**: recorrência de duplicados/divergências após 1-2 meses de disciplina de processo — reabrir para um candidato construído (O-001/O-002/O-003)
- **Decision-changing uncertainties**: U-001, U-009, U-010 (envelope de custo as-is — decide se vale a pena construir em vez de disciplinar)
- **Proof requirement**: (none)
- **Concern notes**: C1 é o que sustenta esta classe na mesa — não é NOT PLAUSIBLE

### O-005 — Não fazer nada, por agora   ·   Não fazer nada / adiar   ·   sem tecnologia
- **Anchored by**: solution-architect
- **Scope**: whole solution
- **Viability**: viable
- **Outcome**: nenhuma alteração ao processo actual; DO-NOTHING desta ronda
- **High-level architecture**: (none) — pedido por email, aprovação por email, registo em folha de cálculo (C-002), sem alteração
- **Assumptions**: A-004, A-005
- **Order of magnitude**: `ORDER OF MAGNITUDE UNAVAILABLE — não há construção; o custo de continuar é o custo do processo actual, ainda não quantificado (U-001, U-009, U-010 em aberto)`
- **Material strengths**: sem compromisso a desfazer; custo de implementação zero
- **Disqualifiers**: (none)
- **Preconditions**: (none)
- **Material trade-offs**: R-003/R-004 continuam sem mitigação nenhuma; M-3 sem mecanismo fiável, sem sequer a disciplina de processo de O-004
- **Material risks**: R-003 (sem mitigação); R-004 (sem mitigação)
- **Cost drivers**: (none)
- **Reversibility**: high
- **Revision condition**: qualquer evento de duplicação/divergência que force decisão (o mesmo gatilho de O-004, mas sem sequer a disciplina intermédia)
- **Decision-changing uncertainties**: U-001, U-009, U-010
- **Proof requirement**: (none)
- **Concern notes**: comparador base para os restantes — nenhum ganho, nenhum custo de mudança

## Parser warnings (if any)
- (none)
