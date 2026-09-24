# F8 — Relatório da fase (pilotos adversariais e aceitação do destinatário)

Estado: **in_progress** — F8.0, F8.1 e F8.2 (execução R3/fx-02) integrados. **Próximo: autorização do mantenedor para as restantes seis execuções (Q5), com o custo real medido em R3** — ver §7. Desenho e decisões Q1–Q5: [DESENHO.md](DESENHO.md).

- Data e responsável: 2026-09-24 · Claude Code, sessão `session_012oqQ6tbYUsoyZT1RPUfpcH`.
- Repositório e branch: `jorgedrestevao/aisa-refactor`, `claude/continua-com-o-plano-xaeq46`. SHA inicial: `1dcdb61` (fim da F7, trazido de `claude/clone-repo-awui-7mmi37` por fast-forward; na altura, `main` não tinha as fases F0–F7 — entraram pelo PR #2, merge `188af41`, 2026-09-24).
- Plano e fase: handoff-v1 v1.2, F8. Autorização: mensagem do mantenedor «Continua com o plano» (2026-09-24), lida como autorização para arrancar a F8 pelo desenho, como a Retoma da F7 prescreve.
- Perfil/schema/pack afectados: F8.1 muda a skill `aisa-blueprint` (passos 15b e 17) e o `CLAUDE.md`; nenhum schema nem pack.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F8.0 Levantamento e desenho | integrado; Q1–Q5 decididas (2026-09-24) | 61cd31b, 5d1ed16 | [DESENHO.md](DESENHO.md). Sondas por subagente (sem escrita): hooks disparam em subagentes; subagente tem `Skill`, não tem `AskUserQuestion` nem `Agent`. Suite: full 111/111, 3033; stdlib 92/92, 2235 |
| F8.1 Preparação dos pilotos | integrado | (este) | Ferramenta `tools/f8.py` (runlog, snapshot save/verify/restore, truth, check-resume, canary, verify-eval, summary; só biblioteca padrão; nunca escreve num engagement) com `test_f8_tools.py` (28 casos; 5 mutantes, 5 apanhados). Protocolo: `protocolo/README.md` (procedimento do orquestrador), `EXECUTOR.md`, `CLIENTE.md`, `DESTINATARIO.md`, `AVALIADOR.md`. Materiais da fx-02 (ajuste por Q5: as outras fixtures preparam-se antes das suas execuções, no F8.3): `fichas/fx-hv1-02.cliente.json` (só fontes e B1/B2 da fx-03), `mudancas/fx-hv1-02-pp-constrained/` (fonte e `expected` M01–M03), `cartoes/R3.json`. **Achado sistémico do levantamento, corrigido antes de correr**: `inventory.py` era o único publicador do âmbito e do inventário e nenhuma skill o chamava — uma sessão real nunca chegava a um pacote. Passos 15b (âmbito, autorizado pelo dono) e 17 (inventário) no `/blueprint`; o `/render` continua sem inventar trabalho nem mudar âmbito. `test_motor_skill_wiring.py` (7 casos: cada comando que publica tem skill que o manda correr; contra a skill anterior, 6 falhas). Deriva do `CLAUDE.md` corrigida (`_work/`, `_design/`). Full 113/113, 3068; stdlib 94/94, 2270 |
| F8.2 Execução R3 (fx-02), primeiro piloto completo | integrado; custo medido, avaliação `pass` — **aguarda autorização do mantenedor para as restantes 6 (Q5)** | (este) | Engagement `f8-r3-fx02`, ponta a ponta: `/start`→`/round` (R-01, 3 rondas de revisor independente até `treated`)→`/frame` (override de gate registado, X-001)→`/options` (5 mandatos, 5 pareceres, 16 achados: 2 `blocking`, 11 `material`, 3 `minor`)→`/decide` (D-002, premortem antes)→`/blueprint` (v01, bloqueado numa escolha estrutural)→mudança injectada a meio (`nota-urgentes.md`, C-003→A-006, U-014)→`/render --all` (release `r0001`, `preliminary`)→2 leituras de destinatário + 1 correcção canónica (release `r0002`)→avaliação assistida (12 itens, `verify-eval` `pass`, canário `clean`). Evidência completa em [execucoes/R3/](execucoes/R3/) (run-log de 175 eventos, `truth-*.json`, `snapshots/*-fim`, `avaliacao.json`, `destinatario-{1,2}.md`, `fim-*.md`). Custo e achados: §7 |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F8.0 | levantamento e desenho | precisa do contexto da sessão; o detalhe volta a ser preciso | na sessão |
| F8.0 | três sondas do ambiente (hook num subagente; `Skill`; `Agent`/`AskUserQuestion`) | independentes; só o veredicto volta | subagente, uma chamada cada |
| F8.1 | ferramenta, protocolo, materiais, ligação das skills | precisa do contexto da sessão | na sessão |

## 3. Decisões do mantenedor (2026-09-24)

| # | Decisão |
| --- | --- |
| Q1 | Executor = subagente novo por segmento; relé literal pelo orquestrador; cliente simulado por fixture |
| Q2 | 7 execuções: fx-01 ×2, fx-02, fx-04, fx-05, fx-03 ×2 sobre cópias da baseline da fx-02 |
| Q3 | O mantenedor é o destinatário real do T46 (um pacote da fx-01 ou da fx-05, fim do F8.3; limite: mantenedor-autor); T45 `not-run` |
| Q4 | Avaliação assistida (código + avaliador independente com locators verificados) validada pelo mantenedor |
| Q5 | Por etapas: fx-02 primeiro, custo real medido, o mantenedor confirma as restantes |

## 4. Auditoria externa (2026-09-24) — os gates da F6 e da F7 reabertos

O mantenedor trouxe uma auditoria ao commit `1dcdb61` com quatro falhas nos gates de entrega; a reprodução desta sessão confirmou-as e encontrou uma quinta da mesma família (A5). Correcção e evidência: [../F7/CORRECAO-AUDITORIA.md](../F7/CORRECAO-AUDITORIA.md).

| Caso | Falha reproduzida |
| --- | --- |
| A1 | um bloco de aceitação só com título e sha sobe o release a `accepted_by_receiver` |
| A2 | âmbito sem `authorized_by`: `inventory.check` diz `SCOPE_NOT_AUTHORIZED`, `release.readiness` diz pronto |
| A3 | FC muda, é republicado e reautorizado; inventário, spec e estimativa antigos continuam prontos |
| A4 | uma edição entre a readiness e a cópia produz um pacote `ready_for_receiver_review` que verifica, com uma estimativa que não passaria |
| A5 | o desenho muda no mesmo caminho e a aprovação é renovada; os FC assentes no sha anterior continuam prontos |

Consequência para esta fase: o passo 15b do `/blueprint` afirma que um âmbito sem autorização mantém o release `preliminary` — passou a ser verdade com a correcção do A2 (`trace.scope_gate` lê o `inventory.check`). Os gates foram aceites de novo a 2026-09-24; o F8.2 arranca numa sessão nova.

## 5. Ambiente

- `cffi` instalado no contentor: sem ele, `test_text_extract.py` falha 3 casos (`ModuleNotFoundError: No module named '_cffi_backend'`, via `pypdf` → `cryptography`). Ambiente, não código; com ele a suite fica igual à do fecho da F7.

## 6. Retoma (para uma sessão nova)

- **Branch**: `main` tem todo o programa (F0–F8.1 e a correcção A1–A5) desde o merge do PR #2 (`188af41`, 2026-09-24). Uma sessão nova parte de `main`.
- **Última operação integrada**: merge do PR #2 em `main` (`188af41`, 2026-09-24), com o registo da nova aceitação dos gates F6/F7 (CI #94 verde em `22c0291`).
- **Ambiente**: `pip install -r requirements-dev.txt`; se `test_text_extract.py` falhar com `_cffi_backend`, `pip install cffi`. Regressão: `python .github/run_tests.py` (esperado 114/114, 3096) e `--list .github/stdlib-tests.txt` (95/95, 2298).
- **Inputs necessários**: `../plan/` (v1.2), [DESENHO.md](DESENHO.md), [protocolo/](protocolo/README.md), fixtures `.claude/tests/fixtures/handoff-v1/`.
- **Resultados recebidos e não integrados**: nenhum. Nenhuma execução-piloto começou; `projects/` não tem engagements (só `.gitkeep`).
- **Próxima acção segura — F8.2, execução R3 (fx-02)**, pelo [protocolo/README.md](protocolo/README.md): cartão [cartoes/R3.json](cartoes/R3.json) (slug `f8-r3-fx02`, segmentos S1, S2 com a pausa cooperativa depois de os candidatos serem publicados, S3, SM com a nota dos urgentes, S4, SC), ficha [fichas/fx-hv1-02.cliente.json](fichas/fx-hv1-02.cliente.json), mudança `mudancas/fx-hv1-02-pp-constrained/`. Executor = subagente novo por segmento; relé literal; cliente simulado continuado por `SendMessage`; snapshot e push a cada fim de segmento (`execucoes/R3/`). O orquestrador conhece os `expected`: não escreve no engagement, não compõe respostas nem achados, e todo o relé fica literal no run-log ([DESENHO.md](DESENHO.md) §1 Papéis e isolamento).
- **No fim do F8.2**: custo real medido (tokens, usos de ferramenta, duração por papel, do run-log) e avaliação assistida (tabela do avaliador + `f8.py verify-eval` + canário) apresentados ao mantenedor.
- **Autorização necessária**: depois do F8.2, o mantenedor confirma as restantes seis execuções com o custo medido (Q5). O T46 (o mantenedor como destinatário real) fica para o fim do F8.3, sobre um pacote da fx-01 ou da fx-05.

## 7. F8.2 — Execução R3 (fx-02): custo real medido e avaliação (para a decisão Q5)

Engagement `f8-r3-fx02`, rota `platform-constrained`. Segmentos S1→S2 (pausa cooperativa)→S3→SM (mudança)→S4→SC, 2 leituras de destinatário, avaliação assistida. Run-log completo: [execucoes/R3/run-log.jsonl](execucoes/R3/run-log.jsonl) (175 eventos). `f8.py summary`:

### 7.1 Custo por papel (tokens / usos de ferramenta / duração — soma do run-log)

| Papel | Chamadas | Tokens | Usos de ferramenta | Duração |
| --- | ---: | ---: | ---: | ---: |
| Executor (por segmento) | 50 | 7 282 952 | 851 | 166,4 min |
| Revisor (lens-coverage, frame, specialist) | 18 | 679 817 | 99 | 30,6 min |
| Cliente simulado | 15 | 1 068 645 | 16 | 6,2 min |
| Destinatário (2 leituras) | 2 | 561 018 | 79 | 10,1 min |
| Avaliador | 1 | 194 142 | 38 | 7,0 min |
| **Total** | **86** | **9 786 574** | **1 083** | **≈ 220 min (3h40) somadas — não é o tempo de relógio** |

Relé: 13 pedidos `pergunta`, 10 pedidos `subagente`. 1 interrupção (pausa cooperativa em S2, cumprida). Mudança injectada (SM). Sessão inteira, do arranque a este relatório: ~10:11–15:06 (≈ 5h de relógio, incluindo o reinício de ambiente a meio que obrigou a relançar cliente e executor de S1).

### 7.2 Avaliação assistida

`avaliacao.json` (12 itens, scenario.json + mudança): **9 cumprido · 2 não_aplicável (bloqueados legitimamente por uma escolha estrutural não relacionada) · 1 ausente · 0 violado**. `f8.py verify-eval` sobre o snapshot final: `pass`, sem achados (todos os locators resolvem). Canário (`f8.py canary`): `clean` — nenhum fragmento distintivo de `scenario.json`/`expected.json` vazou para o engagement.

O único item **ausente** (E06): nenhum artefacto (blueprint, SU, revisão de segurança) nomeia um mecanismo servidor que impeça a chefia de aprovar o seu próprio pedido — M-1 fica citado como invariante de negócio mas nunca como imposição técnica. Acompanha para o F8.3 como padrão a vigiar nas restantes execuções.

### 7.3 O que a execução mostrou (achados reais, não ruído)

- **O revisor independente ganhou o seu lugar.** Em `/round`, a primeira revisão de cobertura apanhou uma lacuna real (critério de sucesso do negócio descartado por engano); a segunda apanhou mais duas (arredondamento mal classificado, envelope de custo as-is nunca escrito). Em `/options`, os 5 especialistas devolveram 16 achados verificáveis — 2 `blocking` (mecanismo de duplicados não idempotente; loja de dados de uma candidata não impõe o limiar financeiro) — nenhum foi ruído: todos com evidência e cenário de falha concretos.
- **Um bloqueio genuíno de arquitectura chegou ao fim da linha.** A aprovação do blueprint ficou presa numa escolha estrutural (integração do catálogo de preços com o ERP-X, `U-004`/`U-012`) que o "dono" simulado não sabia responder, em três perguntas ao longo de S3/S4/SC. Isto é o cenário real que o piloto existe para testar: o aisa correctamente recusou inventar a resposta e recusou aprovar sem ela — `/render --all` produziu só o que a escolha em aberto permite (`discovery-report`, `executive-report`, `solution-blueprint`; `implementation-spec`/`estimate` bloqueados), com o release a sair honestamente `preliminary`.
- **Um bug real do motor, não do engagement.** `coverage.py` entra em impasse quando um `requirement_ref` mal escrito já foi publicado numa revisão anterior: manter o ref dá sempre `COV-DEAD-REF` (mesmo com `disposition: retire`); removê-lo dá `COV-UNREVIEWED`. Sem correcção limpa possível dentro do engagement (append-only); bloqueia `/blueprint --refresh` para sempre nesse caminho. Candidato a fix de kernel antes do F8.3.
- **Uma lacuna real entre o contrato e o código.** `review.py` não tem mecanismo de revalidação quando `shared-understanding.md`/`decisions.md` mudam sob um parecer especialista já publicado (só candidatos/FC/scope/WP têm esse regime) — `handoff-contract.md` → *Pinned dependencies* promete mais do que o código faz. Os dois destinatários apanharam isto de forma independente.
- **A triagem canónica (SC) fez o trabalho que devia fazer.** De 13 lacunas que o primeiro destinatário reportou, 5 eram na verdade o portão a funcionar (não defeitos), 2 eram achados reais mas fora do alcance de correcção unilateral (escalados ao cliente, não fabricados), 1 era achado de kernel fora do âmbito do engagement — só ~7 exigiam mesmo acção. O segundo destinatário, sobre o release corrigido, confirmou o mesmo veredicto estrutural e acrescentou 3 achados novos de menor porte (índice do release incompleto).
- **Anomalia de protocolo, não do aisa**: os executores lançados como chamada única (sem turno intermédio disponível) seguiram directo da retoma ao objectivo do segmento, sem esperar por `CONTINUA F8` — sinalizado pelos próprios executores em S4/SC/2ª tentativa de S2/SM. Não afectou a fidelidade ao protocolo (a retoma foi sempre conferida a posteriori contra a verdade anterior), mas é uma escolha a rever para as próximas 6 execuções: lançar sempre em segundo plano, continuado por `SendMessage`, para preservar o ponto de paragem.
- **Interrupção de ambiente a meio da execução**: um reinício do contentor a meio de S1 obrigou a relançar cliente e executor com verificação contra a verdade anterior (sem perda: o estado não escrito coincidiu). Registado como o cenário de "mudança de sessão" que o próprio programa já antecipava.
- **Nota do orquestrador**: os primeiros 5 `resume_check` deste run-log usam a chave `veredicto` (texto livre) em vez de `verdict: "pass"|"fail"`, que é o que `f8.py summary` conta — por isso o resumo automático mostra `resume_checks.pass: 0/5`, apesar dos 5 não terem nenhuma divergência registada (confirmado por leitura manual, seq 11/45/85/121/144). Corrigido daqui para a frente (a partir da seq 175); fica para as próximas execuções usar o formato certo desde o início.

### 7.4 Decisão pedida ao mantenedor (Q5)

Com este custo medido (≈ 9,8M tokens, ≈ 1 083 usos de ferramenta, ≈ 5h de relógio para um piloto completo com uma mudança a meio), confirmar se avança para as restantes seis execuções (fx-01 ×2, fx-04, fx-05, fx-03 ×2) tal como decidido em Q2, e se o achado de kernel do `coverage.py` (§7.3) se corrige antes de repetir `/blueprint --refresh` nalguma delas.
