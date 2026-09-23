# 01 — Baseline e mapa de alterações

Referência imutável: [repositório no commit inspecionado](https://github.com/jorgedrestevao/aisa/tree/85baf1018ca2b238c41745f7f13dbb539589867f).

Os caminhos nesta página são relativos à raiz do repositório AISA, não ao pacote de planeamento. As propostas não significam que o comportamento já exista.

## O que preservar

| Componente existente | Observação da baseline | Tratamento |
| --- | --- | --- |
| `library/kernel/states.md` | Cinco estados epistémicos; admissão de Unknown e P26 orientadas à decisão técnica | Preservar estados; rever materialidade e compatibilidade |
| `library/kernel/phases.md` | Discovery, Framing, Options, Decision; separação entre várias formas de readiness | Preservar quatro fases; acrescentar marcos de desenho e handoff dentro de Decision |
| `library/kernel/orchestration.md` | Parse-once, contexto seletivo, rounds por lentes e revisão dialética limitada | Preservar ingestão/contexto; substituir obrigatoriedade de agentes no perfil novo |
| `library/kernel/tools/operation.py` | Coordenação de operações e receipts | Reutilizar como único mecanismo de publicação; testar recuperação real |
| `library/kernel/tools/bootstrap.py` | Snapshot de seis autoridades, hashes e seleção de contexto com orçamento | Estender o read-set aos artefactos efetivamente usados pela tarefa |
| `library/kernel/tools/graph.py`, `resolve.py` | Grafo, espelho da SU e reconciliação | Reutilizar identidade e dependências; não criar outro knowledge graph |
| `library/kernel/tools/coverage.py` | Reconciliação, consumo declarado e fingerprints semânticos | Estender rastreabilidade e readiness sem duplicar comparador |
| `library/kernel/tools/projection.py`, `dashboard.py` | Projeções e vistas de estado | Acrescentar vistas; não fazer reescrita transversal como pré-requisito |
| `library/kernel/blueprint-contract.md` | Contrato arquitetural e aprovação do blueprint | Preservar autorização; ligar comportamento funcional à arquitetura |
| `library/kernel/render-contract.md` | Render não é novo processo de decisão | Preservar; desenho em falta volta ao autor, não é inventado pelo renderer |
| `library/packs/pp/pack.yaml` | Pack PP 1.9.0, âmbito centrado em discovery/decisão | Declarar capacidades e perfil handoff; revisão de versão explícita |
| `library/packs/pp/` — research/craft | Conhecimento especializado já separado por função | Reutilizar; melhorar seleção, acesso de revisores e rastreio de versões |
| Templates de arquitetura A1–A12 | Autoridade de dados, segurança, ALM, reversibilidade, operação, economia e provas já contempladas | Completar contratos e ligações; não inventar uma arquitetura paralela |
| `implementation-spec.template.md` no pack PP | Dono das obrigações build/config, inventário, migração, cutover, aceitação e sequência sem durações | Preservar como fonte do trabalho de implementação |
| `estimate.template.md` e `craft/estimation-model.md` | Estimativa é autoridade única de esforço; modo A lê inventário, modo B é condicional | Handoff completo exige modo A; manter modo B para trabalho preliminar |

F0 deve resolver os caminhos completos dos templates por `rg --files`, conservar os nomes canónicos e registar consumidores. Não renomear templates só para seguir a terminologia deste plano.

## Correções estruturais propostas

### B1 — Materialidade demasiado estreita

Na baseline, perguntas são admitidas quando alteram eixos técnicos e Unknown exige alternativas. Isso pode excluir regras funcionais essenciais que não mudam tecnologia, ou factos necessários com um valor ainda desconhecido.

Alterar de forma coordenada `states.md`, `phases.md`, scope de `pack.yaml`, `CLAUDE.md`, skills de captura/análise, arbítrio, validação e testes. Separar tipo de questão e impacto; não baixar uma regra de arredondamento a cosmética só porque não muda a stack.

### B2 — Autoria e revisão na ordem errada

Os rounds de Options podem pôr o arquiteto a criar candidatos enquanto outros agentes já avaliam. O perfil novo exige publicação de uma revisão comum dos candidatos antes da revisão independente. Pareceres anteriores ou sobre revisões diferentes não contam para fecho.

Alterar `orchestration.md`, `.claude/skills/aisa-options/SKILL.md`, agentes e chairman. Reusar limites da revisão dialética, sem ciclos ilimitados de crítica.

### B3 — Pack concentrado no arquiteto

O preâmbulo atual de Options restringe os restantes participantes. No perfil novo, acesso é por mandato e necessidade, não por exclusividade do arquiteto. Research informa viabilidade; craft informa desenho implementável, mas não prova um facto do cliente.

### B4 — Falta de dono inequívoco da semântica funcional detalhada

O renderer já está proibido de inventar transições, regras e detalhes por resolver. Preservar essa proibição e acrescentar autoria funcional a montante. Reusar conteúdo já representado no blueprint; definir contratos funcionais apenas para a semântica que hoje não tem autoridade estruturada clara.

### B5 — Consenso não é evidência

Remover dos mandatos do chairman qualquer inferência do tipo “duas lentes concordam, logo Confirmed”. Concordância pode resolver uma recomendação, não confirmar uma alegação factual.

### B6 — Retoma precisa de cobrir os inputs reais

O snapshot atual protege um conjunto de autoridades, não automaticamente todos os documentos, versões do pack e outputs lidos por qualquer tarefa. Extender os inputs declarados e o controlo de concorrência. Um hook posterior à escrita da SU não torna SU + grafo uma transação indivisível.

### B7 — Readiness de handoff não equivale a solução em produção

O framework já reconhece esse limite. Acrescentar verificação de completude, consistência e receção, sem transformar aprovação de documento em prova de execução.

## Mapa de ficheiros a alterar

| Área | Ficheiros/grupos existentes | Tipo de alteração |
| --- | --- | --- |
| Contratos | `CLAUDE.md`, kernel `states`, `phases`, `orchestration`, `coverage-contract`, `blueprint-contract`, `render-contract`, glossário | Normativa e compatibilidade por perfil |
| Entrada/retoma | skills `aisa-start`, `aisa-orient`, `aisa-status`; comandos start/resume/status | Perfil, rota, scope, próximo trabalho e freshness |
| Análise | skills `aisa-capture`, `aisa-round`, `aisa-frame`, `aisa-answer`, seis `lens-*` | Cobertura sem seis execuções obrigatórias; materialidade ampliada |
| Decisão | `aisa-options`, `aisa-decide`, `aisa-revisit`, `chairman-synthesis`; agentes | Candidatos comuns, revisão seletiva, revisão de decisões |
| Desenho/saída | comandos/skills blueprint, synthesize, render; templates do pack | Autoria funcional explícita, referências de revisão, projeções coerentes |
| Integridade | `operation.py`, `bootstrap.py`, `graph.py`, `resolve.py`, `coverage.py`, `migrate.py` | Read-set, checkpoint, invalidação, compatibilidade |
| Guardas | hooks `pre-authority-guard`, `pre-write-guard`, `on-su-mirror`, `on-su-change`, `phase-gate-check`, `phase-completeness`, `pre-lens-order-check`, `su-confirmed-guard`, `blueprint-validate`, `render-validate`, `synthesis-validate` | Profile-aware; falhas claras; sem promoção silenciosa |
| Observabilidade | `projection.py`, `dashboard.py`, documentação e testes | Blockers por âmbito, tarefas, stale, handoff e métricas |

Os nomes `aisa-capture`/blueprint/render nesta tabela designam a funcionalidade: F0 resolve se a baseline a implementa em comando, skill ou ambos. Não criar duplicados para uniformizar diretórios.

## Novos elementos autorizados pelo desenho

- Um contrato normativo do workflow/perfil e schemas versionados.
- Um módulo fino proposto `library/kernel/tools/workflow.py`, limitado a validar perfil/tarefas/retoma e a chamar serviços existentes. Não é outro motor transacional, grafo ou parser da SU.
- Um artefacto canónico de contratos funcionais por engagement e revisões imutáveis.
- Um checkpoint canónico de trabalho por engagement, publicado pelo coordenador existente.
- Um índice de release/handoff derivado e imutável, com hashes dos outputs e inputs.
- Mandatos/fixtures/testes necessários; nenhuma plataforma de agentes nova.

Se F0 encontrar um dono equivalente já implementado após a baseline, estender esse dono e retirar a criação duplicada através de uma decisão documentada.
