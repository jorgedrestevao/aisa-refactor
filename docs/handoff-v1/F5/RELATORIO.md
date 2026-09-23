# F5 — Relatório da fase (candidatos comuns, especialistas e primeiro percurso vertical)

Estado: **in progress** (2026-09-23). Desenho e decisões Q1–Q6: [DESENHO.md](DESENHO.md). Gate: T25–T30 e o primeiro ensaio T43; revisões na versão certa; zero confirmação por maioria; handoff incompleto rotulado.

## 1. Incrementos

| Inc. | Estado | Commit | Evidência |
| --- | --- | --- | --- |
| F5.1 Candidatos publicados por rota | integrado | 3e12df9 | `library/kernel/tools/review.py` (candidatos: `draft-candidates`, `check-candidates`, `publish-candidates`, `show-candidates`) pelo coordenador, com histórico imutável; schema `handoff-candidates/1`. Integridade: ids, revisão, rota do engagement, premissas na SU; regras por rota — plataforma imposta com `imposition_ref` = autoridade da rota, nenhum candidato fora dela, sem mínimo (T27); `solution-choice` < 3 só com motivo; `change-impact` com baseline e delta. Lacunas visíveis (ordem de grandeza sem fonte, arquitectura, reversibilidade). Rascunhos abertos listados (para T25). `handoff-contract.md` → *Options candidates*. Matriz F0: 3 entradas. `test_review_candidates.py` 10 casos. Full 97/97, 2908; stdlib 78/78, 2110; ambos exit 0 |
| F5.2 Router e mandatos | integrado | (este) | `library/kernel/specialists.md` — dono único dos cinco papéis, das regras do router (bloco `router-rules`) e do contrato de saída. `review.py route`: avalia **todos** os papéis em cada chamada; seleccionado com a evidência (linha viva da SU por lente e termos — nunca estacionada, retirada ou resolvida; marcas do desenho `outside-platform` · `external-access` · `human-surface`; candidato sem ordem de grandeza; `always_in` Options para o revisor de arquitectura) ou não chamado com o que se verificou; headless dispensa UX; determinístico (T28). `review.py mandate`: `_design/reviews/REV-NNNN.mandate.json` pelo coordenador, antes do revisor, com os 12 campos do plano 03, `input_refs` com `sha256` (também read-set) e `knowledge_refs` do pack activo com caminho, `sha256` e `pack_version` (T29, parte do mandato); recusado com `BLOCKING_GAP` sem candidatos publicados ou com rascunho aberto (T25), `INTEGRITY_FAILURE` para papel desconhecido, sem perguntas, ou unidade fora do pack/inexistente. `handoff-contract.md` → *Specialist routing and mandates*. Matriz F0: 3 entradas actualizadas + leitor `blueprint`. `test_review_router.py` 12 casos. Full 98/98, 2920; stdlib 79/79, 2122; ambos exit 0 |
| F5.3 Pareceres, disposições, dialéctica | por fazer | | |
| F5.4 `/options` por rota, `specialist-reviewer`, personas, `/retro` | por fazer | | |
| F5.5 Percurso vertical e ensaio T43 | por fazer | | |
| F5.6 Relatório e gate | por fazer | | |

## 2. Subagentes (README → *Regras de execução*)

| Incremento | Trabalho | Avaliação | Veredicto |
| --- | --- | --- | --- |
| F5.0 | levantamento e desenho | precisa do contexto da sessão; o detalhe volta a ser preciso | na sessão |
| F5.1 | motor, schema, testes | idem | na sessão |
| F5.2 | papéis, router, mandato, testes | idem | na sessão |

## 3. Testes adaptados

- Nenhum em F5.1 nem em F5.2.

## 4. Limitações conhecidas

- A plataforma imposta é declarada no conjunto de candidatos (`imposed_platform`), e o motor exige que a imposição cite a autoridade da rota; o `_state.json` não guarda o nome da plataforma. A comparação é por nome normalizado (maiúsculas/minúsculas e espaços), não por identidade de produto.
- Router por termos (F5.2): os sinais da SU são palavras por lente, declaradas em `specialists.md`; uma linha que descreve o risco sem nenhum dos termos não dispara (ex.: segregação dita como «a chefia nunca aprova um pedido feito por si própria» exigiu os termos `aprov`/`própri`). Mitigação: a avaliação corre sempre e o não chamado mostra o que se verificou, para o autor ou o revisor de arquitectura contestarem. Os FC ainda não são sinal do router (o plano cita-os); fica para quando houver regra que os use.
- O desenho lido pelo router é a versão não-rascunho mais recente, não necessariamente a aprovada; em Options normalmente não há desenho e só a SU e os candidatos sinalizam.
- `specialists.md` refere o agente `specialist-reviewer` por nome até a F5.4 o criar; o caminho é restaurado nessa altura.
