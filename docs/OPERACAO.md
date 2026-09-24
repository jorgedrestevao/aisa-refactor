# aisa — Operação: setup, manutenção, recuperação, acesso e backup

Para quem instala, mantém ou recupera o aisa. Não é o guia de uso (`COMO-USAR.md`) nem a arquitectura (`ARCHITECTURE.md`). Cada comando abaixo existe no código; se um comando aqui não bater com `--help`, o código manda e este ficheiro está desactualizado.

Origem: programa handoff-v1, F7 item 5 (`handoff-v1/F7/DESENHO.md` §3).

## 1. Setup

| Passo | Comando / acção | Verificação |
| --- | --- | --- |
| Dois repositórios | o aisa (código, `library/`, `.claude/`) e um repositório privado de engagements | `ONBOARDING.md` §2.1 |
| Ligar os engagements | `projects/` como junction/symlink para o repositório privado, ou `AISA_ENGAGEMENTS_ROOT` | `ONBOARDING.md` §2.2 |
| Dependências de teste | `python -m pip install -r requirements-dev.txt` (PyYAML, openpyxl, python-docx, pypdf) | a suite stdlib corre sem elas |
| Suite completa | `python .github/run_tests.py` (paralelo; `--sequential` para depurar) | última linha JSON com `fail_files: 0` |
| Suite só stdlib | `python .github/run_tests.py --list .github/stdlib-tests.txt` | idem |
| Instalação | `/status --check` | valida a instalação do aisa |

O CI (`.github/workflows/tests.yml`) corre os dois jobs em Python 3.12 com `fetch-depth: 0`: os testes de compatibilidade extraem código de commits antigos (`ba0c27b`, `56cb4e1`) e falham com uma mensagem clara num clone raso.

## 2. Manutenção

- **`library/` só muda por commit.** Em runtime é só leitura (hook `pre-write-guard.py` + `settings.json deny`). Kernel, schemas, packs e motores mudam por uma alteração revista, com as duas suites verdes antes do push.
- **Um motor novo que lê uma autoridade entra no inventário.** `docs/handoff-v1/F0/consumer-matrix.json`; o teste T02 (`test_handoff_f0.py`) falha se faltar.
- **Um teste novo que só precisa da stdlib entra em `.github/stdlib-tests.txt`.**
- **Uma versão nova de um artefacto** (`schema_version`) muda `workflow.SUPPORTED` e o schema em `library/kernel/schemas/` no mesmo commit. O código anterior recusa a versão nova (`SCHEMA_UNSUPPORTED`) em vez de a ler à sorte. Não há migração automática: a versão histórica fica só leitura (decisão A da F0).
- **Hooks**: `.claude/hooks/HOOKS.md` diz qual bloqueia e qual só regista.

## 3. Recuperação

Primeiro perguntar ao kernel, depois agir. Todos estes comandos são só leitura, excepto os marcados.

| Sintoma | Diagnóstico | Acção |
| --- | --- | --- |
| Uma escrita morreu a meio, ou o `/status` diz «operação pendente» | `python library/kernel/tools/operation.py status --engagement <slug>` | `operation.py recover --engagement <slug>` (**escreve**: termina ou desfaz a operação pelo recibo) |
| O `/status` recusa: estado por reconstruir | `python library/kernel/tools/bootstrap.py --engagement <slug> --json` | a limitação diz a acção que a desbloqueia (`recovery`) |
| O grafo discorda da SU | `python library/kernel/tools/graph.py verify --engagement <slug>` | a SU manda. Para uma edição directa da SU: `resolve.py reconcile --engagement <slug>` mostra o plano; `--apply` publica (**escreve**) |
| Uma peça do desenho assenta numa premissa, num contrato ou num desenho que mudou (`STALE_PREMISE`, `BASIS_CHANGED`, `CONTRACT_CHANGED`) | `python library/kernel/tools/impact.py stale --engagement <slug>` | o autor da peça republica-a com a referência de agora **e a avaliação registada** (`revalidation`: por item `still_valid` ou `updated`, o texto da avaliação, o papel); trocar o hash é recusado (`REVALIDATION_REQUIRED`). Um contrato `updated` volta a pedir autorização do dono; um inventário novo pede nova renderização da spec e da estimativa |
| Um artefacto do desenho sem dependência fixada, fora do histórico ou com um pin mudado sem avaliação (`DEPENDENCY_UNPINNED`, `HISTORY_MISMATCH`, `PIN_UNREVALIDATED`) | `impact.py stale` | republicar pelo motor com a avaliação registada; nunca editar `_design/` à mão nem acertar o histórico |
| O release recusa (`RECOVERY_REQUIRED` ou `STALE_INPUT`) | a mensagem nomeia a limitação ou os ficheiros que mudaram durante o build | recuperar primeiro; ou voltar a construir quando nada estiver a escrever — nada foi publicado |
| Um ficheiro de outra versão (`SCHEMA_UNSUPPORTED`) | a mensagem diz o ficheiro, a versão encontrada e a lida | usar a versão do código que o escreveu, ou corrigir por roll-forward. Nunca editar o `schema_version` à mão |
| Um pacote entregue mudou | `python library/kernel/tools/release.py verify --package <pasta do release>` | um release nunca se reescreve: um build novo cria `r<N+1>` |
| Reverter uma migração | `python library/kernel/tools/migrate.py restore --engagement <slug>` (**escreve**) | só quando nada mudou depois da migração. Com trabalho posterior recusa (`WORK_AFTER`) e diz o que mudou; não há opção para forçar. Reconciliar e seguir em frente |

O que nunca se faz: editar à mão `_graph/`, `_ops/` ou `_migration/` (o guarda recusa: isso apaga a prova de uma operação ou inventa uma); apagar recibos para desbloquear; restaurar um backup sobre um engagement activo.

**Rollback de código.** Voltar o código atrás é seguro só com um leitor que ignora o que não conhece. O código do fim da F5 (`56cb4e1`) escreve num engagement da F6 sem tocar em âmbito, inventário nem releases (provado em `test_f7_compat.py`). A versão histórica (antes do handoff-v1) não escreve num engagement novo: o seu próprio guarda recusa (T36, F1). Quando um leitor antigo não lê o estado, usa-se a versão compatível só para ler e exportar, e corrige-se para a frente.

## 4. Acesso e backup

| O quê | Onde vive | Quem escreve | Backup |
| --- | --- | --- | --- |
| Código, kernel, packs | repositório aisa | commits revistos | o próprio git |
| Estado de cada engagement | `projects/<slug>/` no repositório privado | as skills, pelo coordenador (`operation.py`) | commits e push desse repositório, pelos consultores que o usam |
| Estado coordenado (`_graph/`, `_ops/`, `_migration/`) | dentro do engagement | só `operation.py` | vai com o engagement; nunca se restaura em separado |
| Releases (`_release/r<NNNN>/`) | dentro do engagement | `release.py build` | imutáveis; uma versão obsoleta fica, marcada pela seguinte |
| Memória por papel (`.claude/agent-memory/_universal/`) | repositório aisa | `/retro`, com curadoria humana | o próprio git |
| Memória de tenant (`_tenant/`) | repositório privado | idem | idem |
| Segredos | fora dos ficheiros: cofre ou variável de ambiente (`.env` está no gitignore) | — | o pacote leva a referência, nunca o valor; o coordenador e o `release.py` recusam um valor com padrão de segredo |

Regras de acesso: o repositório privado tem permissões restritas (quem trabalha no engagement); o repositório aisa não guarda nenhum dado de cliente. Quem é dono de cada repositório e com que frequência se faz push não está definido neste código — é decisão de quem opera, e deve ficar escrita no repositório privado.
