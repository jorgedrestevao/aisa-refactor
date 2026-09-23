# F1 — Desenho dos contratos (proposta)

Estado: **Q1–Q6 decididas pelo mantenedor (2026-09-23), todas na opção recomendada (a)**. As I-nn são escolhas internas, revertíveis, com base no plano e registadas para objecção. Implementação pelos incrementos de §4.

Base: plano v1.2 (`../plan/`), F0 (`../F0/RELATORIO.md` §7 defeitos, §11 decisões, §13 decisões do mantenedor). Decisão classic **A**: sem runtime classic na versão nova; engagement sem perfil = legado, só leitura; continua, se preciso, em `jorgedrestevao/aisa@85baf10`.

Convenção: **EXISTE** = verificado no código com `ficheiro:linha`; **PROPOSTO** = a criar.

## 1. Decisões do mantenedor

| Q | Pergunta | Opções | Recomendação → **decisão** | Porquê é do mantenedor |
| --- | --- | --- | --- | --- |
| Q1 | Como impedir a versão histórica de escrever num engagement novo (T36; 07 matriz "Antigo → Handoff novo") | (a) grafo dos engagements `handoff-v1` com `schema_version = 2`; (b) só o campo de perfil em `_state.json`; (c) raiz de engagements diferente | (a) → **(a)** | Muda o contrato do grafo e exclui a versão histórica dos engagements novos |
| Q2 | Vocabulário de rota e despacho no pack e no orquestrador (D15, P10) | (a) nomes do plano (`supported_workflow_profiles`, `supported_routes`, `design_contract_version`) e emendar os 2 testes e `orchestration.md` para distinguir despacho por perfil/rota de encaminhamento por conteúdo; (b) nomes que não colidam (`workflow_profiles.<p>.route_kinds`) e testes intactos | (a) → **(a)** | Muda uma regra de fronteira do orquestrador e dois testes de contrato do pack |
| Q3 | Onde vivem tipo, impacto, âmbito, fecho, bloqueio e referências de uma pergunta (D-F1-02) | (a) colunas novas nas tabelas Unknown/Conflicted da SU; (b) ficheiro lateral indexado pelo id da SU | (a) → **(a)** | Muda o schema da SU, que é a fonte de verdade |
| Q4 | Declaração de âmbito (SCOPE-STATEMENT v1, `CLAUDE.md:5-6`, `pack.yaml:4-5`) | (a) v2 alargada à decisão **e** ao desenho construível; (b) manter v1 | (a), texto em §2.2 → **(a)** | Muda o que o aisa diz que é |
| Q5 | Como se cria um engagement na versão nova enquanto o perfil é experimental | (a) `/start` pergunta sempre o perfil (`AskUserQuestion`: `handoff-v1` experimental, ou sair para a versão histórica); (b) só com `--profile handoff-v1`; sem ele, recusa e aponta a versão histórica | (a) → **(a)** | Muda a entrada do produto durante o rollout |
| Q6 | D02: `/status`, `/resume` e `aisa-orient` escrevem na SU (`aisa-status/SKILL.md:53`) | (a) deixam de escrever; a saúde epistémica passa a ser só calculada e mostrada; (b) manter a escrita só em engagements `handoff-v1` | (a) → **(a)** | Muda o comportamento de um comando de leitura; D-F1-17 pede autorização |

Impacto de cada opção em §2; recomendações fundamentadas no mesmo sítio.

## 2. Contratos por grupo

### 2.1 Perfil, rota, schema, capacidades do pack, erros (D-F1-04/05/06)

**Persistência (PROPOSTO, I-01).** `_state.json` ganha um objecto `workflow`:

```json
"workflow": {
  "profile": "handoff-v1",
  "schema_version": "handoff-state/1",
  "route": "solution-choice | platform-constrained | change-impact",
  "route_revision": 1,
  "route_basis": {"justification": "…", "source_refs": ["C-003"], "authority_ref": "C-003"},
  "route_history": []
}
```

- `profile` não fica à raiz: "profile" já é o perfil de equipa do estimate (EXISTE: `estimate.template.md:177,315-329`).
- Formato de versão dos artefactos novos: `handoff-<nome>/<N>`, como nos exemplos do plano (`examples/work-checkpoint.json`: `handoff-work/1`; `examples/functional-contract.json`: `handoff-functional/1`). Os schemas inteiros existentes ficam como estão (grafo `1`: `graph.py:45`; coverage `1`: `coverage-contract.md:83`) (I-02).
- `route` é escolhida no `/start` (`solution-choice` ou `platform-constrained`). `platform-constrained` exige `authority_ref` para uma linha da SU com a imposição (fonte e autoridade; plano 02 §5). `change-impact` só entra por reabertura sobre baseline aprovada (`phases.md:250-266`, `/revisit`). Mudar a rota cria revisão (`route_revision+1`, entrada em `route_history` com motivo); não se reescreve o histórico.
- Quem muda `workflow`: só o adaptador de `workflow.py` pelo coordenador (`operation.run`). O guarda recusa uma escrita por ferramenta que altere `workflow` ou retire chaves existentes de `_state.json` (I-07).

**Legado (PROPOSTO, I-03).** `_state.json` legível sem `workflow` → legado. Na versão nova, código `UNSUPPORTED_PROFILE`, razão `legacy_profile_absent`, acção seguinte "ler aqui; continuar em `aisa@85baf10`". Leitura permitida (`/status`, `/dashboard`, `/resume`); escrita recusada sem tocar em nada. Não se reutiliza `LEGACY_MODE`, que significa "sem `_graph/`" (EXISTE: `bootstrap.py:300-317`). `_state.json` ausente = engagement a nascer (regra actual de `pre-authority-guard.py:138-140`).

**Q1 — vedação contra a versão histórica.**
- (a) EXISTE hoje: `graph.read` devolve `unsupported_schema` para `schema_version != 1` (`graph.py:303-307`). O `bootstrap` fica não pronto (`bootstrap.py:318-324`) e o `pre-authority-guard` recusa a escrita (`:144-146`, `:197`). A versão histórica **é** este código, por isso um grafo `schema_version = 2` nos engagements novos faz a versão histórica recusar escrever-lhes pelos seus próprios guardas e motores. Na versão nova, `graph.py` lê `2` (engagements `handoff-v1`) e lê `1` só para leitura de legado. O schema 2 reserva os tipos de dependência de 04 (§2.5), que a versão histórica também não entenderia. Custo: `graph.py`, `migrate.init` (nasce em 2), testes do grafo. Limite: escritas por `Bash` (`mv` de `_state.json.tmp`) não passam por hooks, na versão histórica e na nova. Fica escrito como limitação.
- (b) A versão histórica ignora o campo e escreve à vontade. É confiar numa guarda inexistente, o que o plano 07 proíbe.
- (c) Mudar a raiz de `projects/` mexe em `CLAUDE.md`, hooks, skills e na montagem do repositório privado. É um custo grande para o mesmo efeito.

**Capacidades do pack (Q2, I-04).**
- `pack.yaml` do PP declara `supported_workflow_profiles: [handoff-v1]`, `supported_routes: [solution-choice, platform-constrained, change-impact]`, `design_contract_version: 1` e sobe `pack_version` para 1.10.0.
- Os packs skeleton (generic/mendix/outsystems) não declaram nada → `UNSUPPORTED_PROFILE`, sem fallback (T04).
- Colisão EXISTE: `test_pp_deliverable_templates.py:1341-1344` recusa qualquer linha activa com `routes:` (apanha `supported_routes:`); `test_pp_pack_integrity.py:124-139` recusa `route`/`routes` dentro de `deliverables[]` e mapas de encaminhamento à raiz; `orchestration.md:113` proíbe o orquestrador de "become a routing or rules engine".
- (a) Emenda:
  - o primeiro teste passa a recusar a **chave** `routes:` (regex de chave, não substring);
  - o segundo fica como está, porque as chaves novas vivem à raiz e fora de `deliverables[]`;
  - `orchestration.md` ganha a distinção: despachar o passo seguinte por perfil/rota declarados é permitido; decidir por conteúdo (relevância de evidência, arquitectura, template por outcome) continua proibido;
  - o plano usa "router" nesse sentido (02 §2: "Retoma, router e observabilidade").
- (b) Evita tocar nos testes, mas diverge dos nomes normativos do plano (02 §1).

**Erros (I-05).** `workflow.py` define o envelope `{ok, code, reasons[], affected_ids[], input_revision, next_actions[]}` e os 8 códigos estáveis. Os códigos existentes não mudam de nome: são embrulhados, com o original preservado em `reasons[].source_code`. Mapa:

| Código estável | Origem actual (EXISTE) |
| --- | --- |
| `RECOVERY_REQUIRED` | operação pendente/interrompida (`bootstrap.py:292-298`; `operation.py` `PENDING_EXISTS`, `PENDING_UNREADABLE`, `STAGING_*`, `THIRD_STATE`) |
| `INTEGRITY_FAILURE` | `GRAPH_INTEGRITY`, `invalid_format`, `incoherent_pair`, `unreadable`, `AUTHORITY_DRIFT`, `AUTHORITY_UNMIRRORED`, `VERIFY_FAILED`, `RECEIPT_MISMATCH`; grafo ausente num engagement `handoff-v1` |
| `SCHEMA_UNSUPPORTED` | `unsupported_schema` (`graph.py:56`), coverage `unsupported`, `workflow.schema_version` desconhecido |
| `STALE_INPUT` | `BASE_CHANGED` (`operation.py`), `PLAN_STALE`, `CONCURRENT_WRITE` |
| `UNSUPPORTED_PROFILE` | novo: legado; perfil não declarado pelo pack |
| `INCOMPLETE_READ_SET`, `AUTHORIZATION_REQUIRED`, `BLOCKING_GAP` | novos (F2, F4, F6); contrato fixado em F1 |

**Resolver único (I-06).** Uma função pura `workflow.profile_of(eng)` em `library/kernel/tools/workflow.py`, chamada por:
- os hooks (pelo mesmo mecanismo `runpy` com que já carregam `bootstrap.py`: `pre-authority-guard.py:51,142`);
- `_common.py`;
- `operation.run`, que é a porta única dos motores que publicam (`operation.py:465`).

**Enforcement do legado só-leitura (T03).**
1. PreToolUse `Skill`: skills que escrevem, sobre engagement legado → recusa com `UNSUPPORTED_PROFILE` antes de qualquer escrita (o `matcher: Skill` já existe em `settings.json`).
2. PreToolUse `Write|Edit` (`pre-authority-guard`):
   - legado → recusa;
   - passa a reconhecer `_state.json.tmp`, que hoje escapa: o nome não está em `AUTORIDADES` (`pre-authority-guard.py:56,104`);
   - recusa sempre escrita por ferramenta em `_graph/`, `_ops/`, `_migration/`, `_work/` e `_design/`, mesmo com bootstrap pronto (D05).
3. `operation.run`: recusa publicar em legado.

A regeneração do `dashboard.html` (derivado) continua.

### 2.2 Materialidade (D-F1-02)

**Dono único: `states.md`.** Substitui a admissão P-26: três declarações, oito eixos (EXISTE: `states.md:133-148`). Com a opção A não há regra dupla, porque na versão nova só escrevem engagements `handoff-v1`. Mantêm-se:
- regra do papel (P-21);
- relato de terceiro (P-23);
- ignorância da organização;
- três destinos;
- perguntas de custo;
- custo/swing como economia da pergunta (princípio 9).

Admitir uma pergunta quando a resposta pode alterar ≥ 1 dos cinco aspectos (plano 02 §4):
1. solução/arquitectura, que inclui os oito eixos actuais;
2. correcção funcional, cálculo, transição, excepção ou resultado;
3. aceitação, obrigação contratual ou evidência;
4. segurança, privacidade, operação, suporte, migração ou recuperação;
5. viabilidade, dependência, custo ou esforço material.

Tipos:
- `fact_gap`: facto em falta, sem alternativas fabricadas (T06);
- `design_choice`: alternativas quando existem;
- `conflict`;
- `proof_obligation`.

Cada pergunta tem impacto, âmbito afectado, papel que responde, condição de fecho e referências.

**Bloqueio ≠ prioridade.**
- `criticidade` + `swing` = prioridade.
- Coluna nova `bloqueio` ∈ {`blocks_all`, `blocks_scope`, `delegated_choice`, `implementation_proof`, `—`} (`—` = não bloqueia).
- `implementation_proof` cujo resultado possa invalidar a viabilidade é `blocks_scope` ou `blocks_all` antes do compromisso (02 §8).
- Marcas `observed_as_is` / `proposed_to_be` / `authorized_to_be` na coluna de âmbito, sem estados novos.

**Estacionar (I-10).** Sem impacto demonstrável → marca sancionada `— estacionada (<motivo>)`, que qualquer escritor pode pôr, com motivo obrigatório. É reversível e não conta como fechada (T07). A retirada P-21 continua só do dono.

**Q3 — onde vivem os campos.**
- (a) Colunas novas. Unknown: `id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | ronda`. Conflicted ganha `impacto | âmbito | quem decide | fecho | bloqueio | referências`.
  - EXISTE: o parser único lê pelo cabeçalho e guarda todas as células (`dashboard.py:629-643,705` `raw`), por isso uma SU antiga continua a ler-se.
  - `bloqueio` é campo material: espelhado no grafo e comparado pelo `drift` (F2).
  - A SU continua legível por si, que é a regra "sponsor can read SU".
- (b) Ficheiro lateral: duas fontes para a mesma pergunta e reconciliação permanente; a SU deixa de ser legível sozinha.

**Q4 — SCOPE-STATEMENT v2 (texto proposto).** "aisa runs discovery on a process to reach a grounded technical decision and a design a delivery team can build without guessing: which technology and pattern, against which alternatives, at what cost, and which behaviour, acceptance and operation. It is not an open-ended business-discovery platform; a question is admitted only when its answer can change the decision, the functional behaviour, the acceptance, the operation or the effort." Em `CLAUDE.md:5`, `pack.yaml:4-5` e nos restantes ficheiros que citam v1 (inventário em F0 §11). Com v1 mantida, T05 (a regra de arredondamento que não muda tecnologia) seria inadmissível.

**Escritores e testes do P-26: adaptar no mesmo incremento.**
- Escritores: 6 lentes, `aisa-round` 5f (árbitro), `chairman-synthesis` 4b, `aisa-answer`, `aisa-capture` (`PM-U`), faceta de admissão do `dashboard.py`, memória dos agentes, `CLAUDE.md:106`.
- Testes: `test_admission_rule`, `test_arbiter_declarations`, `test_technical_decision_refocus` s02/s12, `test_retirement` (contrato).
- Os casos de `fixtures/technical-decision-refocus/admission-cases.md` servem de ponto de partida (F0 `fixture-registry.json`).
- As linhas antigas nunca são reclassificadas automaticamente.

### 2.3 Evidência e dialéctica (D-F1-03, D-F1-13)

**Regra.** `Confirmed` só pelo limiar de `states.md` (localizador de uma das classes + afirmação ao nível da prova). O número de personas que concordam nunca muda um estado epistémico (T08; 07 "o que não inferir"). Retirar:
- `chairman.md:17` ("often becomes Confirmed");
- `chairman-synthesis/SKILL.md:115` (regra 3, "≥2 persona anchors");
- a 1.ª linha da tabela do Step 3, que muda para "localizador de classe → Confirmed; senão Assumed com base".

**Dialéctica.**
- A síntese aceite resolve só recomendação/disposição, nunca um facto. Divergência factual sem prova → `Conflicted`. Divergência de recomendação → *finding* com disposição.
- Limite em 3 divergências × 2 chamadas (EXISTE: Step 2b). Esgotar o limite → escalar, nunca aceitar por esgotamento (T30).

**Findings (I-09).**
- Reutilizar `resolve.finding`/`dispose_finding` (EXISTE: `resolve.py:532-561`; nó do grafo com histórico).
- As disposições passam de `disposed|reopened` para: `accepted` · `corrected` · `rejected_with_evidence` · `delegated` · `escalated` · `deferred`, com base obrigatória. `reopened` mantém-se.
- Não há motor novo.

**Enforcement determinístico (T08, D19).**
- Em engagements `handoff-v1`, uma escrita na SU que acrescente **ou promova no lugar** uma linha `Confirmed` sem localizador de classe é recusada antes de escrever (PreToolUse sobre o conteúdo novo comparado com o actual).
- Hoje o `su-confirmed-guard` só avisa, depois de escrever, e só para ids `C-` novos.
- É integridade, e o plano manda que falhe fechado (02 §9). O princípio 5 do `CLAUDE.md` ("the only hard rule is library/ read-only") já não descreve o runtime (o `pre-authority-guard` bloqueia desde P7.5). Passa a dizer: gates de fase suaves; integridade fecha.

### 2.4 Prontidão, frescura, tarefas, checkpoint, revisão (D-F1-08/09)

**Checkpoint (I-08).**
- Admitido como índice de trabalho do próprio aisa, só com referências: `_work/checkpoint.json`, schema `handoff-work/1` (estrutura do exemplo do plano).
- Emendar `orchestration.md:92` ("No handoff-summary artefact"): o checkpoint não resume conhecimento do engagement; aponta para tarefas, resultados e autoridades por id e revisão.
- `aisa-status/SKILL.md:104` fica: o bloco `Read to resume` continua calculado e não persistido.
- Publicado pelo coordenador (F2).

**Estados.**
- Tarefa: `planned|running|blocked|completed|cancelled`.
- Resultado: `draft|received|integrated|superseded`.
- Frescura: `current|stale|unverified`. O `not_evaluated` do coverage lê-se como `unverified`.
- Autorização = referência ao acto e à autoridade, ou `null`.

**Predicados.**
- Chave nova `handoff_readiness`, calculada por `workflow.evaluate_readiness`. Traz `decision_ready`, `design_ready`, `handoff_ready`, `integrity_ok`, `required_approvals_present`, `receiver_review_complete` e `receiver_accepted`, cada um `true|false|unverified` com razões.
- O objecto `readiness` actual (as quatro respostas de `phases.md:240-247`) fica e alimenta `design_ready`.
- Nunca um verde único.
- Aprovação = propriedade de revisão + âmbito (hash), nunca de um nome de ficheiro (D11).

**Interfaces.**
- Assinaturas e schemas de request/response de `plan_review`, `evaluate_readiness` e `build_resume_plan` congelados em F1, como documento e schema.
- Implementação nas fases que os usam (F2 retoma, F4 revisão, F6 prontidão). Não se escreve código-esqueleto antes.

### 2.5 Guardas por perfil, coverage por lente, dependências (D-F1-07/10/12)

**Guardas (I-11).**
- `pre-lens-order-check`, `phase-completeness` e `phase-gate-check` passam a perguntar o perfil ao resolver:
  - legado → não intervêm (a escrita é recusada nos pontos de §2.1);
  - `handoff-v1` → comportamento actual até F3 substituir o fluxo das passagens. Aí saem, conforme a disposição de F0 (`pre-lens-order-check` e `phase-completeness`: eliminar; `phase-gate-check`: adaptar).
- Os testes de ordem fixa ficam até F3, porque testam o fluxo ainda em uso.
- O critério "≥ 3 opções" do gate passa a depender da rota em F4.
- Ligar guardas novas só depois de testadas em diretório temporário (F0 P3: correm na sessão que implementa).

**Coverage por lente (I-12).**
- Etapa nova `lenses` do `coverage.py` (reutiliza motor, registos e frescura), por dimensão: `assessed|gap|not_applicable`, com referências.
- `not_applicable` sem motivo é inválido (T07).
- `orchestration.md:112,125` continua certo para os sinais do pack (não são cobertura).
- Implementação em F3.

**Dependências (I-13).** O grafo schema 2 aceita `rel` ∈ {`supports`, `constrains`, `implements`, `verifies`, `estimates`, `derived_from`} ao lado de `was`/`depends_on` (EXISTE: `resolve.py:571`). Não se fundem os tipos antigos em silêncio. Emendar `orchestration.md:90` ("never through a dependency graph or a new field") para `handoff-v1`. Uso em F5/F6.

### 2.6 FC / J / WP, handoff completo, Options por rota, acesso ao pack (D-F1-11/14)

**Namespaces (I-14).**
- `FC-NNNN`, `J-NNNN`, `WP-NNNN`, `TASK-NNNN`, `SCOPE-NNNN`. Todos livres no runtime; `J-1` só aparece num relatório antigo em `docs/`.
- Carimbados pelo coordenador ao publicar, nunca pelo render.
- Nunca reutilizados: o artefacto guarda `retired_ids`.

**Posse.**

| Artefacto | Dono de |
| --- | --- |
| blueprint | topologia, entidades, `record_authority`, definição lógica de campo (`blueprint-contract.md:19`) |
| `_design/functional-contracts.json` (`handoff-functional/1`) | semântica de comportamento, com referências a ids do blueprint e da SU |
| implementation-spec | `WP` (build, config, migração, prova, aceitação), com referências a FC e blueprint |
| estimate | único dono do esforço, por `WP` |

As outras 7 fontes de esforço (D12) passam a "banda preliminar (modo B)" rotulada ou saem (F5). "Completo para handoff" é redefinido no contrato de render em F5/F6.

**Options por rota.**
- `solution-choice`: candidatos realmente aplicáveis; um só candidato viável é admitido com motivo.
- `platform-constrained`: variações dentro da plataforma imposta e viabilidade, sem alternativas artificiais; incompatibilidade declarada (T27).
- `change-impact`: delta, raio de impacto, decisões a reabrir.
- Texto em `phases.md` em F1; `dashboard`/`aisa-options` em F4.

**Acesso ao pack.** Por mandato de papel, com `knowledge_refs` registados (F3/F4). A neutralidade de Discovery/Framing mantém-se por fase (`no-tech-mention-before-options`).

## 3. Schemas congelados em F1

| Schema | Caminho proposto | Conteúdo |
| --- | --- | --- |
| `handoff-state/1` | `library/kernel/schemas/handoff-state.schema.json` | bloco `workflow` de `_state.json` |
| `handoff-pack/1` | `library/kernel/schemas/handoff-pack.schema.json` | chaves de capacidade do `pack.yaml` |
| `handoff-work/1` | `library/kernel/schemas/handoff-work.schema.json` | checkpoint, tarefas, resultados |
| `handoff-functional/1` | `library/kernel/schemas/handoff-functional.schema.json` | FC, com campos N/A com motivo |
| `handoff-index/1` | `library/kernel/schemas/handoff-index.schema.json` | índice de entrega (projecção de uma revisão) |
| `handoff-response/1` | `library/kernel/schemas/handoff-response.schema.json` | envelope e códigos |

Regras comuns:
- `schema_version`, `engagement_id`, `revision`, `based_on[]` (revisão/hash dos inputs) e `items[]` nos artefactos canónicos (02 §3).
- `additionalProperties` nunca apaga: o validador reporta campos desconhecidos e preserva-os.
- Validador: subconjunto de JSON Schema em `workflow.py`, só com biblioteca padrão (ADR-001), limitado às palavras-chave usadas.

## 4. Incrementos de implementação (depois de Q1–Q6)

| Inc. | Conteúdo | Testes / cenários |
| --- | --- | --- |
| F1.4 | `workflow.py` (`profile_of`, `validate_profile`, envelope, validador), schemas, capacidades do pack (Q2), `/start` com perfil e rota (Q5), grafo schema 2 (Q1) | T03 (identificação), T04, T36, testes de schema; adaptar testes do pack e do grafo no mesmo commit |
| F1.5 | Enforcement do legado só-leitura (Skill, Write/Edit com `_state.json.tmp` e directórios coordenados, `operation.run`); D02 (Q6) | T03 (recusa sem alteração de dados), D05 |
| F1.6 | Materialidade (Q3, Q4): `states.md`, escritores do P-26, parser, SCOPE v2 | T05, T06, T07; adaptar testes P-26 no mesmo commit |
| F1.7 | Evidência: chairman, dialéctica, findings, guarda de promoção | T08, T30 (contrato) |
| F1.8 | Textos normativos de 2.4–2.6, tabela leitor/escritor/schema, alterações incompatíveis, relatório | T35 = recusa segura (opção A); gate |

Cada incremento: comandos de regressão (`run_tests.py` e `--list .github/stdlib-tests.txt`), commit e push; `library/` por script administrativo.
