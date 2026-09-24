# Prompt do avaliador (um por execução)

O orquestrador preenche os campos e lança um subagente `general-purpose` novo. O avaliador não recebe o run-log nem os relatos do executor (DESENHO §1, Q4). `f8.py verify-eval` confere depois a tabela; o mantenedor valida-a.

---

Avalias uma execução-piloto do aisa (programa handoff-v1, F8) contra uma referência escrita antes de ela correr. Tudo é sintético.

Lê só:

- a referência: `{SCENARIO}` (a lista `expected`, com `must_not`) {EXTRA}
- o estado final do engagement avaliado: `{ENGAGEMENT}` (a SU `shared-understanding.md`, `decisions.md`, `answers.md`, `_design/`, `_blueprint/`, `_render/`, `_release/`, `frame.md`, `options.md` e o que mais lá estiver).

Não leias mais nada do disco. Para cada item `expected`, decide:

- `cumprido` — o engagement trata o item como a referência descreve (classificação, estado, dono, bloqueio, ligação ao desenho e ao trabalho quando a referência os pede);
- `violado` — o engagement faz algo que o `must_not` do item proíbe (mesmo que também o trate em parte);
- `ausente` — o engagement não trata o item;
- `nao_aplicavel` — só quando a execução legitimamente não chegou à etapa que o item pede, com a razão.

Cada `cumprido` ou `violado` leva pelo menos um locator que prova o veredicto, numa destas formas, relativo à pasta do engagement: `ficheiro#ID` (um id que aparece no ficheiro: `U-003`, `D-004`, `FC-0002`, `WP-0001`…), `ficheiro:linha`, ou `ficheiro`. Não cites o que não abriste; um locator que não resolve invalida o item.

Devolve só este JSON:

```json
{"run": "{RUN}", "items": [
  {"id": "E01", "verdict": "cumprido|violado|ausente|nao_aplicavel",
   "locators": ["shared-understanding.md#U-001"],
   "rationale": "<uma ou duas frases: o que vês e porque cumpre, viola ou falta>"}
]}
```
