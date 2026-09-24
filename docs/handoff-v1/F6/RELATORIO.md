# F6 — Relatório da fase (rastreabilidade completa e handoff implementável)

Estado: **gate avaliado — aguarda aceitação** (2026-09-24). Desenho e decisões Q1–Q8: [DESENHO.md](DESENHO.md). Gate: T31–T34, T37–T40; zero requisito material órfão no âmbito entregue; esforço por WP coerente; pacote parcial nunca apresentado como completo.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F6.1 Âmbito e inventário | integrado | 564197a | `library/kernel/tools/inventory.py` (`draft` · `check` · `publish` · `show`, `--kind scope\|work-packages`) pelo coordenador, com histórico imutável; schemas `handoff-scope/1` e `handoff-work-packages/1`. Integridade: ids, revisão, incluídos que resolvem (SU, jornadas de FC), exclusão só com `D-NNN` que existe (T33, parte do motor), WP com FC e nós do desenho resolvidos pelo resolvedor de selectores do `coverage.py` (um nó exacto), `proves` só obrigações de prova, dependências sem ciclo, nenhum campo de esforço (Q2). Lacunas visíveis: âmbito sem autorização, WP sem `realizes`/`acceptance`/DoD. `handoff-contract.md` → *Work packages and completeness*. Matriz F0: 5 entradas. `test_inventory.py` 13 casos. Full 102/102, 2950; stdlib 83/83, 2152; ambos exit 0 |
| F6.2 Rastreabilidade | integrado | 5d182ed | `library/kernel/tools/trace.py show` (só leitura): cadeia âmbito → requisito → FC → nó do desenho → WP → aceitação/prova, órfãos nos dois sentidos (`NO_CONTRACT` — N1, `NO_WORK`, `NO_TEST`, `NO_DESIGN_REASON`); exclusão autorizada sem achado; um requisito realizado directamente por um WP não é órfão. T31: cada obrigação de prova do desenho com WP (`proves`, selector por índice ou chave) e aceitação. T34: pergunta em aberto `proof_obligation` bloqueia o compromisso mesmo com trabalho planeado (`states.md` l. 172). T37: headless → interface «não aplicável», sem achado de ecrã. `handoff-contract.md` → *Traceability*. Matriz F0: 2 entradas. `test_trace.py` 9 casos. Full 103/103, 2959; stdlib 84/84, 2161; ambos exit 0 |
| F6.3 Estimativa, gate de âmbito, N2/N3/S6 | integrado | 724e4ef | **T32**: `trace.py estimate-check`/`backlog-check` — linhas de tabela que citam `WP-NNNN` + revisão do inventário citada; achados `STALE_INVENTORY`, `NO_INVENTORY_REVISION`, `UNKNOWN_WP`, `UNESTIMATED_WP`/`MISSING_IN_BACKLOG`, `DUPLICATE_ESTIMATE`; `--spec`: duração numa linha do inventário da spec → `EFFORT_IN_SPEC` (uma regra de negócio com «dias» não conta). **T33/N4**: `trace.py scope-gate` → `complete`/`partial`/`blocked`; bloqueiam achados de rastreio, FC incluído não autorizável ou não autorizado, `blocks_all` aberta; parcial exige coerência (`WORK_FOR_EXCLUDED`, `DEPENDS_ON_EXCLUDED`, `REQUIRED_FIELD_WITHOUT_PRODUCER` — o caso `valor_total` do 2.º ensaio). **N2**: `functional.py approval-block` gera a aprovação do desenho com `**Blueprint sha256**`; `blueprint_approval_state` `current`/`stale`/`unverified`/`missing`; `render_gate` bloqueia `stale` e `unverified`; `/blueprint` passo 15 usa o motor. **N3**: `functional.show` → `warnings` (`UNDEFINED_FIELD_REF`, `ACTOR_NOT_IN_DESIGN`) — no percurso da F5 apanha o actor «Chefia» do FC-0003. **S6**: `states.md` fixa `¶n` num `.md` = número do `[¶n]` do `text_extract.py`; as citações das fixtures da F3–F5 estavam desfasadas (convenção «título conta») e foram corrigidas; `test_locator_convention.py` confere 21 citações. Contratos: `handoff-contract.md` (*Estimate, backlog and the scope gate*), `blueprint-contract.md` (aprovação). `test_scope_gate.py` 13 casos, `test_locator_convention.py` 3. Full 105/105, 2975; stdlib 86/86, 2177; ambos exit 0 |
| F6.4 Templates | integrado | ffad224 | `implementation-spec.template.md`: autoridades `work-packages.json` (inventário, sem duração) e `scope.json`; transformação `work-packages.json item -> inventory row`; §1 ganha *Inventário de trabalho (inventário r<N>)* com a tabela WP·propósito·realiza·prova·depende de·aceitação·DoD (slots condicionais `work_package_inventory`, `inventory_revision`, com condição e fonte); §14 dependências = `depends_on`; §15 T38 (reconciliação, cutover, rollback, retenção cada um com WP e aceitação, ou N/A). `estimate.template.md`: modo A lê `work-packages.json` na revisão citada; §3 uma linha por WP com `inventário r<N>`. `/render` passo 7c (`trace.py show`/`scope-gate` antes, `estimate-check --spec` depois; bloqueiam a versão real). `render-validate.py` regista os achados de inventário (`MISSING_IN_SPEC`, `EFFORT_IN_SPEC`, `UNESTIMATED_WP`…). `test_templates_inventory.py` 10 casos. T38 executável fica para o F6.6 (fx-hv1-05). Full 106/106, 2985; stdlib 87/87, 2187; ambos exit 0 |
| F6.5 Release, segredos, aceitação | integrado | 25728fd | `library/kernel/tools/release.py`: `build` → `_release/r<NNNN>/` imutável (autoridades, `_design/`, desenho aprovado, fontes, spec e estimativa mais recentes, contratos e schemas, unidades dos mandatos, leituras dos motores) + `handoff-index.json` válido; **nível calculado** (`preliminary` com motivos; `ready_for_receiver_review` só com rastreio, gate de âmbito, spec, estimativa e aprovação do desenho a passar). `verify` (T39): alterado, em falta, a mais. **Segredos** (T40): `operation.run` recusa `SECRET_IN_CONTENT` (padrões fechados; referência de cofre passa; o valor nunca aparece na recusa); `build`/`verify` repetem. **Aceitação** (Q6): `acceptance-block` com `**Release sha256**`, validador humano, `**Simulated**`; `status` sobe a `accepted_by_receiver` só com bloco real sobre release que verifica. `/render` passo 10b. `handoff-contract.md` → *Release*. Matriz F0: 4 entradas. `test_release.py` 9 casos; os testes existentes sem falso positivo de segredo; um falso positivo real (o próprio contrato a descrever a atribuição de password) foi corrigido — valor entre crases é menção, não segredo. Full 107/107, 2994; stdlib 88/88, 2196; ambos exit 0 |
| F6.6 Percursos e 3.º ensaio T43 | integrado (ensaio simulado) | 51bb79e, 9b6a021 + (este) | `test_hv1_release_paths.py` (7): **fx-hv1-02** percurso da F5 + âmbito D-005 + inventário + pré-visualizações rotuladas (só inventário, sem esforço) + `release.py build` → `preliminary` com motivos (C-001 sem contrato — N1; `valor_total` sem produtor — N4), pacote verifica; **fx-hv1-05** T38 executável (reconciliação, cutover, coexistência, rollback, normalização, retenção com WP e aceitação; tirar o rollback ou a sua aceitação → achado); **fx-hv1-04** T37 no pacote (sem obrigação de ecrã). Pacote congelado `F6/pacote-fx-hv1-02/` (39 ficheiros, código `51bb79e`). **3.º ensaio T43** (`F6/T43-ENSAIO.md`): 13 usos, ~110 k tokens, 137,6 s; 17 lacunas; integridade verificada pelo destinatário sem o motor; N1/N4 lidos do pacote; 4 lacunas sistémicas novas **R1–R4** (autorizações em falta no índice, `reviews_basis` perdido, pergunta `blocks_scope` sem ligação invisível ao gate, datas incoerentes com o build) |
| F6.6b Correcção R1–R4 | integrado | 70cd22d + (este) | R1 `authorization_refs` com âmbito, exclusões, autoridade da rota e escolha; R2 `reviews_basis` reposto; R3 `UNLINKED_BLOCKING_QUESTION` no gate (U-002 passa a bloquear o parcial até ser citada ou excluída); R4 decisão posterior ao build em `limitations`. Pacote regenerado (`F6/pacote-fx-hv1-02/`, código `70cd22d`); o pacote do 3.º ensaio fica no histórico (`9b6a021`). Sem 4.º ensaio (decisão do mantenedor). Full 108/108, 3004; stdlib 89/89, 2206; ambos exit 0 |
| F6.7 Relatório e gate | integrado | (este) | §5–§9. Full 108/108, 3004; stdlib 89/89, 2206; ambos exit 0. CI #69 (desenho) a #77 verdes; #78 (pacote regenerado) em fila no fecho |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F6.0 | levantamento e desenho | precisa do contexto da sessão; o detalhe volta a ser preciso | na sessão |
| F6.1 | motor, schemas, testes | idem | na sessão |
| F6.2 | motor, testes | idem | na sessão |
| F6.3 | motores, contratos, fixtures | idem | na sessão |
| F6.4 | templates, skill, hook | idem | na sessão |
| F6.5 | motor, coordenador, testes | idem | na sessão |
| F6.6 | percursos e pacote | idem | na sessão |
| F6.6 | destinatário do 3.º ensaio T43 | independente: só o pacote | **subagente**, uma chamada (DESENHO §0) |
| F6.6b | correcção R1–R4, pacote | precisa do contexto da sessão | na sessão |
| F6.7 | relatório e gate | precisa do contexto da sessão; é a evidência da fase | na sessão |

## 3. Testes adaptados

- Nenhum em F6.1 nem em F6.2.
- F6.6b — adaptados: os cenários «parcial coerente» (`test_scope_gate`) e «pronto» (`test_release`) passam a excluir a U-002 com autorização — sem isso o R3 bloqueia-os, e bem.
- F6.3 — adaptados: citações `¶` das fixtures corrigidas para a numeração do extractor (`test_hv1_02_discovery`, `test_functional_authorization`, `test_hv1_design_path`, `test_hv1_vertical`, `test_review_candidates`, `test_trace`); o helper de aprovação do desenho (`test_functional_render.approve_blueprint`) leva o `sha256`; `test_blueprint_functional_step` lê os comandos do motor em vez de uma lista fixa.

## 4. Limitações conhecidas

- Uma referência a um nó do desenho por índice (`proof_obligations[0]`) resolve, mas move-se se a lista for reordenada; o contrato do coverage (§5.1) pede o `sha256` do alvo nesse caso, e o inventário ainda não o guarda.
- `trace.py` liga a obrigação de prova ao WP pelo selector de `proves` (índice ou `chave=valor`); um índice move-se se a lista do desenho for reordenada (mesma limitação do F6.1).
- T34 lê as perguntas em aberto `proof_obligation` da SU; uma obrigação de prova do desenho com `funded: no` ainda não é bloqueio por si.
- N4 identifica o produtor de um campo pelas referências `<domínio>.<campo>` nas pós-condições dos FC; um FC que produz o campo sem o nomear assim não conta como produtor (conservador: aparece como incoerência).
- O teste de convenção dos `¶` aceita a citação se existir numa das fontes com o mesmo nome (há dois `pedido.md`, fx-hv1-02 e fx-hv1-04).
- O pacote experimental da F5 (`F5/pacote-fx-hv1-02/`) é histórico: leva as citações antigas e a aprovação sem impressão digital; o pacote da F6 é gerado de novo em F6.6.
- Os padrões de segredo são fechados e estritos: um segredo num formato fora da lista (por exemplo uma chave sem prefixo conhecido escrita em prosa) não é apanhado. A prova T40 cobre `password=`, chaves privadas, tokens de fornecedores conhecidos e `Bearer`.
- O nível `ready_for_receiver_review` confere estrutura (rastreio, âmbito, inventário, aprovação); a qualidade do conteúdo continua a ser dos revisores e do destinatário.

## 5. Gate (05_FASES F6: T31–T34, T37–T40; zero requisito material órfão no âmbito entregue; esforço por WP coerente; pacote parcial nunca apresentado como completo)

| Teste | Critério (06_VALIDACAO) | Estado | Evidência |
| --- | --- | --- | --- |
| T31 | Obrigação arquitectural de prova → mapeada a trabalho e condição de aceitação | **cumprido** | `test_trace.Provas`: obrigação do desenho sem WP (`proves`) ou sem aceitação → achado; obrigação provada nomeia o WP. `inventory.py` recusa `proves` que não aponte uma obrigação de prova (`test_inventory.Inventario`) |
| T32 | Backlog/estimativa discordam do inventário → referências/revisões inconsistentes detectadas; sem esforço concorrente | **cumprido** | `test_scope_gate.Estimativa`: `UNESTIMATED_WP`, `DUPLICATE_ESTIMATE`, `UNKNOWN_WP`, `STALE_INVENTORY`, `NO_INVENTORY_REVISION`, `MISSING_IN_BACKLOG`; `EFFORT_IN_SPEC`. O inventário recusa campos de esforço (`test_inventory` Q2). `render-validate.py inventory_gaps` e `/render` 7c (`test_templates_inventory`) |
| T33 | Subconjunto com bloqueio de build → entrega total bloqueada; parcial só com exclusão autorizada e dependências coerentes | **cumprido** | `test_scope_gate.GateDeAmbito` (bloqueio num incluído → `blocked`; parcial coerente → `partial`; `WORK_FOR_EXCLUDED`, `DEPENDS_ON_EXCLUDED`, `REQUIRED_FIELD_WITHOUT_PRODUCER`; `blocks_all` aberta; R3 `UNLINKED_BLOCKING_QUESTION`); exclusão sem `D-NNN` recusada na publicação (`test_inventory.Ambito`) |
| T34 | Prova futura pode invalidar viabilidade → bloqueia compromisso; não escondida em checklist | **cumprido, com limite** | `test_trace.Provas.test_t34_*`: `proof_obligation` em aberto bloqueia mesmo com WP planeado. Limite: lê as perguntas da SU; obrigação do desenho com `funded: no` ainda não bloqueia por si |
| T37 | Solução headless → nenhuma UI/documento de ecrãs obrigatório sem aplicabilidade | **cumprido** | `test_trace.Headless` (interface «não aplicável», sem achado de ecrã); `test_hv1_release_paths.Fx04Headless` (o pacote não deve ecrã) |
| T38 | Migração de legado → reconciliação, cutover, rollback e retenção ligados a trabalho/aceitação | **cumprido, com limite** | `test_hv1_release_paths.Fx05Migracao` (cada obrigação com WP e aceitação; sem rollback ou sem a sua aceitação → achado); spec §15 (`test_templates_inventory`). Limite: prova ao nível do motor, sobre inventário escrito pelo teste; nenhum render real de migração |
| T39 | Ficheiro alterado depois do release → hash mismatch; release não aceite como intacta | **cumprido** | `test_release.Verificacao.test_t39_*` (alterado, a mais, em falta); `test_release.Aceitacao` (release adulterada não é aceite nem se mantém aceite) |
| T40 | Segredo em rascunho/output → bloqueado; referência segura preservada | **cumprido, com limite** | `operation.run` recusa `SECRET_IN_CONTENT` → `INTEGRITY_FAILURE`, sem o valor na recusa; `Password=<vault:…>` passa; `release.build` recusa segredo numa fonte e não cria `_release/` (`test_release.Verificacao.test_t40_*`). Limite: lista fechada de padrões (§4) |
| Zero requisito material órfão no âmbito entregue | — | **cumprido** | `ready_for_receiver_review` exige zero achados de `trace.py` (`test_release.Build`); os órfãos N1 (C-001 sem contrato) e N4 (`valor_total` sem produtor) mantêm o pacote da fixture `preliminary` com o motivo (`test_hv1_release_paths.Fx02Pacote`; `F6/pacote-fx-hv1-02/handoff-index.json` → `readiness.reasons`) |
| Esforço por WP coerente | — | **cumprido** | inventário sem esforço (Q2); estimativa = único dono do esforço, uma linha por WP na revisão citada (T32); `estimate-check --spec` no `/render` 7c bloqueia a versão real |
| Pacote parcial nunca apresentado como completo | — | **cumprido** | nível calculado, nunca declarado (`preliminary` com motivos); `scope_gate` distingue `complete`/`partial`/`blocked`; `exclusions` com motivo e `D-NNN` no índice; `receiver_acceptance: null` até bloco real; `accepted_by_receiver` só com bloco não simulado sobre release que verifica (`test_release.Aceitacao`); pré-visualizações rotuladas (`Fx02Pacote`) |
| T43 (3.º ensaio) | Destinatário em contexto novo identifica trabalho e testes; lacunas registadas | **cumprido como ensaio simulado** | `T43-ENSAIO.md`: 17 lacunas, integridade verificada sem o motor; R1–R4 corrigidas em F6.6b (sem 4.º ensaio, decisão do mantenedor — a correcção é provada pelos testes `test_release.IndiceDoRelease` e `test_scope_gate`, não por releitura) |

Suites no fecho: full 108/108 ficheiros, 3004 testes; stdlib 89/89, 2206; ambos exit 0. CI #69 a #77 verdes; #78 (`67eb645`, pacote regenerado, sem mudança de código) em fila no fecho deste relatório.

## 6. Itens do plano (05_FASES F6)

| # | Trabalho | Estado | Onde |
| --- | --- | --- | --- |
| 1 | Estender templates conforme `08_HANDOFF.md`; não criar onze documentos | feito | spec e estimativa estendidos (F6.4); nenhum documento novo; `scope.json`/`work-packages.json` são autoridades, não deliverables |
| 2 | Requisito/regra → FC → elemento arquitectural → WP → teste/prova; órfãos e não aplicável | feito | `trace.py` (F6.2), nos dois sentidos; exclusão autorizada e headless sem achado |
| 3 | Spec dona do inventário, estimativa única dona do esforço; backlog deriva do inventário | feito | inventário estruturado projectado pela spec (Q1); `estimate-check`/`backlog-check` (F6.3) |
| 4 | ALM, security enforcement, integração/recovery, migração/cutover, operação e dependências do cliente quando aplicáveis | feito, com limite | spec §7–§11 e §15 já existiam; F6.4 liga §15 (reconciliação, cutover, rollback, retenção) a WP e aceitação, ou N/A; limite: só o pack `pp` tem templates de deliverable; os outros packs não têm spec |
| 5 | Índice de handoff com hashes, revisões lidas, âmbito incluído/excluído, aprovação e limitações | feito | `release.py build` → `handoff-index/1` com `files` (sha256), `based_on`, `reviews_basis` (R2), `scope_refs`/`exclusions`/`scope_definition`, `authorization_refs` (R1), `limitations` (R4) |
| 6 | Gates por âmbito e aceitação do destinatário independente da prontidão técnica | feito | `scope_gate` (F6.3); `acceptance_block`/`status` (F6.5): prontidão calculada e aceitação são campos distintos |
| 7 | Obrigações de prova com trabalho e aceitação, sem afirmar execução não ocorrida | feito | T31/T34; `proofs.performed: []` no índice; `**Simulated**` no bloco de aceitação |

**Entregável**: pacote completo para o âmbito contratado — o mecanismo está feito e provado; o pacote da fixture `fx-hv1-02` sai, correctamente, `preliminary`, porque a fixture tem órfãos reais (C-001, U-002, `valor_total`).

**Rollback** (plano: suspender a publicação final; conservar rascunhos/revisões e explicar obsolescência): deixar de chamar `release.py build` e o `/render` 10b; `_design/history/` e cada `_release/r<NNNN>/` são imutáveis e ficam; um release obsoleto não verifica (T39) ou tem revisão posterior — o índice diz porquê. Os motores novos (`inventory.py`, `trace.py`, `release.py`) saem por `git revert` sem tocar nas autoridades.

## 7. Leitor, escritor e schema — o que F6 acrescenta

| Artefacto | Escritor | Leitores | Schema |
| --- | --- | --- | --- |
| `_design/scope.json` + `_design/history/scope.r<NNNN>.json` | `inventory.py publish --kind scope` (coordenador) | `trace.py`, `release.py`, `/render` (spec), `render-validate.py` | `handoff-scope/1` |
| `_design/work-packages.json` + `_design/history/work-packages.r<NNNN>.json` | `inventory.py publish --kind work-packages` (coordenador) | `trace.py`, `release.py`, spec (projecção do inventário), estimativa (modo A), `render-validate.py` | `handoff-work-packages/1` (sem esforço) |
| leituras de rastreio (`trace.json`, `scope-gate.json` no pacote) | `trace.py` (só leitura; copiadas por `release.py`) | `/render` 7c, `release.py`, destinatário | — |
| `_release/r<NNNN>/` + `handoff-index.json` | `release.py build` (revisão nova; nunca por cima) | `release.py verify`/`status`, destinatário | `handoff-index/1` |
| bloco de aprovação do desenho em `decisions.md` (`**Blueprint sha256**`) | `functional.py approval-block` → `resolve.py publish` | `blueprint_approval_state`, `render_gate`, `release.py` | `blueprint-contract.md` |
| bloco `D-NNN — Aceitação do destinatário` em `decisions.md` | `release.py acceptance-block` → `resolve.py publish` | `release.py status` | `handoff-contract.md` → *Release* |
| recusa de segredo | `operation.run` (antes de qualquer escrita) | todos os escritores do coordenador | código `SECRET_IN_CONTENT` → `INTEGRITY_FAILURE` |

## 8. Decisões e pontos por decidir

- Tomadas (mantenedor, 2026-09-23/24): Q1–Q8 do desenho; 3.º ensaio no fecho; corrigir R1–R4 sem 4.º ensaio.
- Desvios registados: nenhum ao plano. `docs/ARCHITECTURE.md` e `docs/ONBOARDING.md` continuam desactualizados (vêm da F5; não nomeiam `inventory.py`, `trace.py`, `release.py`).
- Limites declarados (§4 e §5): T34 sem `funded: no`; T38 ao nível do motor; T40 lista fechada; N4 por referências pontuadas; prontidão estrutural; pré-visualizações escritas pelo teste; selector por índice sem `sha256` do alvo.
- Em aberto desde a F5: os FC como sinal do router (limite de T28) — não foi trabalho da F6.

## 9. Próxima fase

F7 — mudanças, migração e compatibilidade (`../plan/05_FASES.md`): raio de impacto e stale transitivo sobre o grafo/fingerprints (o selector por índice sem `sha256` do alvo entra aqui), migração dry-run com cópia validada, rejeição segura de versões não suportadas. Arranca com o seu `DESENHO.md` (§0 dos subagentes) e as decisões de contrato ao mantenedor.
