# F8 — Relatório da fase (pilotos adversariais e aceitação do destinatário)

Estado: **in_progress** — F8.0 e F8.1 integrados. **F8.2 suspenso**: a auditoria externa de 2026-09-24 reabriu os gates da F6 e da F7 (A1–A5, reproduzidos nesta sessão); os pilotos correm depois da correcção. Desenho e decisões Q1–Q5: [DESENHO.md](DESENHO.md).

- Data e responsável: 2026-09-24 · Claude Code, sessão `session_012oqQ6tbYUsoyZT1RPUfpcH`.
- Repositório e branch: `jorgedrestevao/aisa-refactor`, `claude/continua-com-o-plano-xaeq46`. SHA inicial: `1dcdb61` (fim da F7, trazido de `claude/clone-repo-awui-7mmi37` por fast-forward; `main` não tem as fases F0–F7).
- Plano e fase: handoff-v1 v1.2, F8. Autorização: mensagem do mantenedor «Continua com o plano» (2026-09-24), lida como autorização para arrancar a F8 pelo desenho, como a Retoma da F7 prescreve.
- Perfil/schema/pack afectados: F8.1 muda a skill `aisa-blueprint` (passos 15b e 17) e o `CLAUDE.md`; nenhum schema nem pack.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F8.0 Levantamento e desenho | integrado; Q1–Q5 decididas (2026-09-24) | 61cd31b, 5d1ed16 | [DESENHO.md](DESENHO.md). Sondas por subagente (sem escrita): hooks disparam em subagentes; subagente tem `Skill`, não tem `AskUserQuestion` nem `Agent`. Suite: full 111/111, 3033; stdlib 92/92, 2235 |
| F8.1 Preparação dos pilotos | integrado | (este) | Ferramenta `tools/f8.py` (runlog, snapshot save/verify/restore, truth, check-resume, canary, verify-eval, summary; só biblioteca padrão; nunca escreve num engagement) com `test_f8_tools.py` (28 casos; 5 mutantes, 5 apanhados). Protocolo: `protocolo/README.md` (procedimento do orquestrador), `EXECUTOR.md`, `CLIENTE.md`, `DESTINATARIO.md`, `AVALIADOR.md`. Materiais da fx-02 (ajuste por Q5: as outras fixtures preparam-se antes das suas execuções, no F8.3): `fichas/fx-hv1-02.cliente.json` (só fontes e B1/B2 da fx-03), `mudancas/fx-hv1-02-pp-constrained/` (fonte e `expected` M01–M03), `cartoes/R3.json`. **Achado sistémico do levantamento, corrigido antes de correr**: `inventory.py` era o único publicador do âmbito e do inventário e nenhuma skill o chamava — uma sessão real nunca chegava a um pacote. Passos 15b (âmbito, autorizado pelo dono) e 17 (inventário) no `/blueprint`; o `/render` continua sem inventar trabalho nem mudar âmbito. `test_motor_skill_wiring.py` (7 casos: cada comando que publica tem skill que o manda correr; contra a skill anterior, 6 falhas). Deriva do `CLAUDE.md` corrigida (`_work/`, `_design/`). Full 113/113, 3068; stdlib 94/94, 2270 |

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

Consequência para esta fase: o passo 15b do `/blueprint` afirma que um âmbito sem autorização mantém o release `preliminary` — passou a ser verdade com a correcção do A2 (`trace.scope_gate` lê o `inventory.check`). O F8.2 espera pela nova aceitação dos gates.

## 5. Ambiente

- `cffi` instalado no contentor: sem ele, `test_text_extract.py` falha 3 casos (`ModuleNotFoundError: No module named '_cffi_backend'`, via `pypdf` → `cryptography`). Ambiente, não código; com ele a suite fica igual à do fecho da F7.

## 6. Retoma (para uma sessão nova)

- Última operação integrada: F8.1 (preparação dos pilotos).
- Inputs necessários: `../plan/` (v1.2), [DESENHO.md](DESENHO.md), fixtures `.claude/tests/fixtures/handoff-v1/`.
- Resultados recebidos e não integrados: nenhum.
- Ambiente: `pip install -r requirements-dev.txt` e, se `test_text_extract.py` falhar com `_cffi_backend`, `pip install cffi`; regressão `python .github/run_tests.py` (esperado 111/111, 3033).
- Próxima acção segura: a correcção A1–A5 está integrada ([../F7/CORRECAO-AUDITORIA.md](../F7/CORRECAO-AUDITORIA.md)); com os gates da F6/F7 de novo aceites pelo mantenedor, o F8.2 (execução R3, fx-02) pelo `protocolo/README.md`.
- Autorização necessária: nova aceitação dos gates F6/F7 depois da correcção; depois do F8.2, o mantenedor confirma as restantes execuções com o custo medido (Q5).
