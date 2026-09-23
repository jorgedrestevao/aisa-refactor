# Programa handoff-v1 — estado e retoma

Este directório acompanha a refatorização "handoff-v1" do AISA. Uma sessão nova continua a partir daqui, sem a conversa que a produziu.

| O quê | Onde |
| --- | --- |
| Plano (direcção de trabalho, v1.2, com MANIFEST e validador) | [plan/README.md](plan/README.md) |
| Fases, gates e rollback | [plan/05_FASES.md](plan/05_FASES.md) |
| Relatório da fase F0 (**concluída**; decisões, testes, retoma) | [F0/RELATORIO.md](F0/RELATORIO.md) |
| Fase corrente | **F1** (autorizada em 2026-09-23, em curso) — [F1/RELATORIO.md](F1/RELATORIO.md) |
| Artefactos de F0 | [F0/](F0/) |
| Fixtures sintéticas do programa | `.claude/tests/fixtures/handoff-v1/` |
| Teste de F0 (T02 + fixtures) | `.claude/tests/test_handoff_f0.py` |

## Regras de leitura

- O plano é a direcção de trabalho. Os contratos em produção só mudam com o trabalho faseado de F1 em diante, registado no relatório de cada fase.
- O plano de evolução anterior (`docs/evolution/`, P0–P8) não é uma dependência deste programa. Os seus testes e mecanismos são reutilizados só quando servem os cenários deste plano, e os seus estados de aprovação ou bloqueio não se herdam (plano, README e 09).
- Cada fase só avança com autorização explícita do mantenedor. O estado corrente e a próxima acção segura estão na secção *Retoma* do relatório da última fase.

## Regras de execução

- **Workflows paralelos (subagentes) só para tarefas que não precisam do contexto da sessão e cujo detalhe não acrescenta nada à sessão** (regra do mantenedor, 2026-09-23). Servem: varrimentos mecânicos, inventários, verificações de consistência, testes de refutação de uma afirmação já escrita. Ficam na sessão: tudo o que depende das decisões do mantenedor, e tudo cujo detalhe a implementação a seguir precisa (desenho de contratos, código, testes, decisões a apresentar ao mantenedor). Na dúvida, fica na sessão. Circunstância: em F1.3 o desenho dos contratos foi lançado como workflow paralelo (6 desenhadores + revisão); o mantenedor fixou esta regra e o workflow foi parado sem resultados integrados ([F1/RELATORIO.md](F1/RELATORIO.md) §3).

## Ambiente de testes

A suite precisa de PyYAML, openpyxl, python-docx e pypdf. O runtime continua a precisar só da biblioteca padrão. Comando de regressão:

```
python .github/run_tests.py
```

A baseline de referência e a divergência conhecida com o job de CI estão em [F0/test-baseline.json](F0/test-baseline.json).
