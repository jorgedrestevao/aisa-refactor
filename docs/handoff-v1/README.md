# Programa handoff-v1 — estado e retoma

Este directório acompanha a refatorização "handoff-v1" do AISA. Uma sessão nova continua a partir daqui, sem a conversa que a produziu.

| O quê | Onde |
| --- | --- |
| Plano (direcção de trabalho, v1.2, com MANIFEST e validador) | [plan/README.md](plan/README.md) — cópia idêntica ao zip enviado pelo mantenedor (sha256 `70aa0f4a6fe28557…`, `diff -r` sem diferenças, 2026-09-23). O zip vive nos uploads da sessão, que são efémeros; a cópia versionada é a referência. |
| Fases, gates e rollback | [plan/05_FASES.md](plan/05_FASES.md) |
| Relatório da fase F0 (**concluída**; decisões, testes, retoma) | [F0/RELATORIO.md](F0/RELATORIO.md) |
| Relatório da fase F1 (**concluída**; contratos, perfil, legado só-leitura, admissão, evidência) | [F1/RELATORIO.md](F1/RELATORIO.md) · [desenho](F1/DESENHO-CONTRATOS.md) · [leitor/escritor/schema](F1/LEITOR-ESCRITOR.md) |
| Relatório da fase F2 (**concluída**; continuidade transacional: read-set, rascunho e publicação, checkpoint, retoma a frio) | [F2/RELATORIO.md](F2/RELATORIO.md) · [desenho](F2/DESENHO.md) |
| Relatório da fase F3 (**concluída**; análise integrada, cobertura das seis perspectivas, `/frame` com revisor independente) | [F3/RELATORIO.md](F3/RELATORIO.md) · [desenho](F3/DESENHO.md) |
| Relatório da fase F4 (**concluída**; contratos funcionais, autorização, coerência com o desenho, render) | [F4/RELATORIO.md](F4/RELATORIO.md) · [desenho](F4/DESENHO.md) |
| Relatório da fase F5 (**concluída**; candidatos por rota, especialistas por mandato, primeiro percurso vertical) | [F5/RELATORIO.md](F5/RELATORIO.md) · [desenho](F5/DESENHO.md) · [ensaios T43](F5/T43-ENSAIO.md) |
| Relatório da fase F6 (**concluída; gate reaberto pela auditoria de 2026-09-24 e corrigido — aguarda nova aceitação**; âmbito e inventário, rastreabilidade, gate de âmbito, release com índice, segredos, aceitação do destinatário) | [F6/RELATORIO.md](F6/RELATORIO.md) · [desenho](F6/DESENHO.md) · [ensaio T43](F6/T43-ENSAIO.md) |
| Relatório da fase F7 (**concluída; gate reaberto pela auditoria de 2026-09-24 e corrigido — aguarda nova aceitação**; raio de impacto e stale derivado, versões suportadas, restore sem força, rollback, docs de operação) | [F7/RELATORIO.md](F7/RELATORIO.md) · [desenho](F7/DESENHO.md) |
| Relatório da fase F8 (**em curso**; pilotos adversariais e aceitação do destinatário) | [F8/RELATORIO.md](F8/RELATORIO.md) · [desenho](F8/DESENHO.md) |
| Fase corrente | **F8**, iniciada a 2026-09-24 na branch `claude/continua-com-o-plano-xaeq46`: desenho decidido (Q1–Q5) e preparação dos pilotos (F8.1) integrados. **Gates da F6 e da F7 reabertos** pela auditoria externa de 2026-09-24 (A1–A5) e **corrigidos** ([F7/CORRECAO-AUDITORIA.md](F7/CORRECAO-AUDITORIA.md)); aguardam a nova aceitação do mantenedor, e só então o F8.2 (primeiro piloto) |
| Artefactos de F0 | [F0/](F0/) |
| Fixtures sintéticas do programa | `.claude/tests/fixtures/handoff-v1/` |
| Teste de F0 (T02 + fixtures) | `.claude/tests/test_handoff_f0.py` |

## Regras de leitura

- O plano é a direcção de trabalho. Os contratos em produção só mudam com o trabalho faseado de F1 em diante, registado no relatório de cada fase.
- O plano de evolução anterior (`docs/evolution/`, P0–P8) não é uma dependência deste programa. Os seus testes e mecanismos são reutilizados só quando servem os cenários deste plano, e os seus estados de aprovação ou bloqueio não se herdam (plano, README e 09).
- Cada fase só avança com autorização explícita do mantenedor. O estado corrente e a próxima acção segura estão na secção *Retoma* do relatório da última fase.

## Regras de execução

- **Mudança de sessão** (mantenedor, 2026-09-24). A sessão avisa o mantenedor quando deve abrir uma sessão nova: depois de uma compactação do contexto, e no fecho de cada incremento quando a conversa já vai longa. Antes de avisar, deixa a *Retoma* do relatório da fase corrente actualizada e com push, para a sessão nova começar só pelos ficheiros.
- **Subagentes — regra do refactor inteiro** (mantenedor, 2026-09-23). Antes de definir ou lançar **qualquer** subagente, avalia-se: ele precisa do contexto da sessão (ou de quem o lança) para correr, ou é independente? Só é subagente o que é independente **e** cujo detalhe não precisa de voltar — só o veredicto. O que precisa do contexto, ou cujo detalhe alimenta o passo seguinte, corre na sessão (inline). Na dúvida, na sessão. Vale em dois planos, pela mesma regra:
  - **Execução do refactor.** Servem varrimentos mecânicos, inventários, verificações de consistência e testes de refutação de uma afirmação já escrita. Ficam na sessão: tudo o que depende das decisões do mantenedor, e tudo cujo detalhe a implementação a seguir precisa (desenho de contratos, código, testes, decisões a apresentar). Circunstância: em F1.3, o desenho dos contratos foi lançado como workflow paralelo (6 desenhadores + revisão); o mantenedor fixou esta regra e o workflow foi parado sem resultados integrados ([F1/RELATORIO.md](F1/RELATORIO.md) §3).
  - **Desenho do framework** (personas, revisores, especialistas, rondas de antítese no runtime do aisa). Serve sobretudo a revisão independente, onde a independência é o próprio benefício. Cada fase regista a avaliação no §0 do seu `DESENHO.md`, para cada subagente que define, mantém ou retira. Primeiro inventário: [F3/DESENHO.md](F3/DESENHO.md) §0.

## Ambiente de testes

A suite precisa de PyYAML, openpyxl, python-docx e pypdf. O runtime continua a precisar só da biblioteca padrão. Comando de regressão:

```
python .github/run_tests.py
```

A baseline de referência e a divergência conhecida com o job de CI estão em [F0/test-baseline.json](F0/test-baseline.json).
