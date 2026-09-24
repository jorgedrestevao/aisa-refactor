# F8 — Relatório da fase (pilotos adversariais e aceitação do destinatário)

Estado: **in_progress — desenho** (F8.0). Decisões Q1–Q5 por decidir: [DESENHO.md](DESENHO.md).

- Data e responsável: 2026-09-24 · Claude Code, sessão `session_012oqQ6tbYUsoyZT1RPUfpcH`.
- Repositório e branch: `jorgedrestevao/aisa-refactor`, `claude/continua-com-o-plano-xaeq46`. SHA inicial: `1dcdb61` (fim da F7, trazido de `claude/clone-repo-awui-7mmi37` por fast-forward; `main` não tem as fases F0–F7).
- Plano e fase: handoff-v1 v1.2, F8. Autorização: mensagem do mantenedor «Continua com o plano» (2026-09-24), lida como autorização para arrancar a F8 pelo desenho, como a Retoma da F7 prescreve.
- Perfil/schema/pack afectados: nenhum até ao F8.1.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F8.0 Levantamento e desenho | integrado; decisões por tomar | (este) | [DESENHO.md](DESENHO.md). Sondas por subagente (sem escrita): hooks disparam em subagentes; subagente tem `Skill`, não tem `AskUserQuestion` nem `Agent`. Suite: full 111/111, 3033; stdlib 92/92, 2235 |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F8.0 | levantamento e desenho | precisa do contexto da sessão; o detalhe volta a ser preciso | na sessão |
| F8.0 | três sondas do ambiente (hook num subagente; `Skill`; `Agent`/`AskUserQuestion`) | independentes; só o veredicto volta | subagente, uma chamada cada |

## 3. Ambiente

- `cffi` instalado no contentor: sem ele, `test_text_extract.py` falha 3 casos (`ModuleNotFoundError: No module named '_cffi_backend'`, via `pypdf` → `cryptography`). Ambiente, não código; com ele a suite fica igual à do fecho da F7.

## 4. Retoma (para uma sessão nova)

- Última operação integrada: commit do desenho F8.0 nesta branch.
- Inputs necessários: `../plan/` (v1.2), [DESENHO.md](DESENHO.md), fixtures `.claude/tests/fixtures/handoff-v1/`.
- Resultados recebidos e não integrados: nenhum.
- Ambiente: `pip install -r requirements-dev.txt` e, se `test_text_extract.py` falhar com `_cffi_backend`, `pip install cffi`; regressão `python .github/run_tests.py` (esperado 111/111, 3033).
- Próxima acção segura: obter do mantenedor as decisões Q1–Q5 do desenho; registá-las no DESENHO.md; só então o F8.1.
- Autorização necessária: Q1–Q5.
