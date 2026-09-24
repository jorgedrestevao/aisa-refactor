# FIM DE SEGMENTO F8 — R3 / S4

**feito:**
- Corri `/render --all` (skill `aisa-render`) sobre `f8-r3-fx02`, seguindo os passos da skill um por um: pré-render (`coverage.py check --stage render`), activação por deliverable, produção, `render-validate.py`, revisão de cobertura `stage=render` publicada por `coverage.py finalize`, log de corrida, episódio em `story.md`.
- Produzidos 3 de 6 deliverables (os que a activação autoriza nesta escolha):
  - `_render/f8-r3-fx02_discovery-report_v01.md`
  - `_render/f8-r3-fx02_executive-report_v01.md`
  - `_render/f8-r3-fx02_solution-blueprint_v01.md` (arquitectura autorizada — âmbito "solução completa"; ambas as candidatas do catálogo de preços apresentadas, nenhuma escolhida)
- Bloqueados (não produzidos, com o que desbloqueia): `implementation-spec`, `claude-design-brief` — o blueprint v01 não está aprovado (1 escolha estrutural em aberto: U-004/U-012); desbloqueia fechando essa escolha e aprovando o blueprint.
- Não aplicável (skip, não é lacuna): `estimate` — nem o Modo A (especificação aprovada, que não existe) nem o Modo B (estimativa de planeamento por candidato, que exige também uma necessidade material do sponsor por magnitude comparativa, não registada nesta corrida) resolvem.
- `render-gaps.md` e `render-log.md` escritos de raiz (primeira corrida do engagement). 5 lacunas registadas, cada uma com owner (`evidence` para `solution_name` no discovery-report; `architecture` para 4 secções A4.3/A4.4/A8/A9/A10 do blueprint sem conteúdo registado no desenho — não inventado conteúdo para as fechar).
- Corrida a revisão de cobertura `stage: render` para os três documentos publicados (`coverage.py finalize`), à mão via as funções internas do motor (não há CLI de alto nível para montar o rascunho): `_coverage/coverage_v15.json` (discovery-report), `_coverage/coverage_v16.json` (solution-blueprint), `_coverage/coverage_v18.json` (executive-report) — as três `coverage: gaps` / `eligible: false`, reflectindo honestamente que as revisões a montante (`coverage_v13.json`, `coverage_v09.json`) também não estão fechadas.
- Construído o release: `python library/kernel/tools/release.py build --engagement f8-r3-fx02` → `_release/r0001/handoff-index.json`. **`delivery_level: "preliminary"`, calculado pelo motor** (nível não alterado, lacunas não preenchidas para o subir). Razões que o motor deu: 1 achado de rastreabilidade, gate de âmbito bloqueado (`BLOCKS_ALL_OPEN` ×1, `PROOF_WITHOUT_WORK` ×1, `UNLINKED_BLOCKING_QUESTION` ×4), implementation-spec e estimativa não renderizadas, aprovação do desenho em falta.

**estado:** fase `decision`, ronda `D-01` (inalteradas — `/render` não muda fase). Publicado: `discovery-report v01`, `executive-report v01`, `solution-blueprint v01`; release `r0001` (`preliminary`).

**perguntas abertas e bloqueios:** a escolha estrutural do catálogo de preços (U-004/U-012) continua a bloquear a aprovação do blueprint e, por consequência, a Especificação de Implementação, o Claude Design Brief e a Estimativa. Perguntas materiais por levar ao cliente (agenda), literais:
1. De onde deve vir o preço do catálogo de equipamento — leitura em tempo real do ERP-X ou cópia própria replicada? (U-004)
2. O ERP-X expõe interface programável (API/OData/BD) para ler o catálogo de preços? (U-012)
3. Que mecanismo regista quem aprovou o quê e quando, de forma fiável? (U-006)
4. As 5 populações têm licenciamento suficiente para o ambiente governado, ou é preciso adquirir mais? (U-011)
5. Em que contexto os colaboradores pedem hoje equipamento — secretária, terreno, dispositivo, ligação? (U-002)
6. A aplicação nativa está instalável/licenciada nos dispositivos dos requerentes? (U-013)
7. O caminho de urgência salta também a aprovação da direcção financeira acima do limiar de 5000€? (X-001, Critical — fecha por `/answer X-001 "..."`)

**próximo passo que o aisa indica:** fechar a escolha estrutural (U-004/U-012) e obter aprovação de negócio do blueprint → então `/render --all` de novo produz `implementation-spec`, `claude-design-brief` e (se um dos dois modos resolver) `estimate`, e o release seguinte pode subir de nível.

**anomalias (literais):**
1. `library/kernel/tools/coverage.py` não tem um comando que construa sozinho um rascunho de revisão `stage: render` (basis/target/manifesto sim, via `compute_basis`/`build_manifest`; o array `coverage[]` semântico não) — o executor montou-o por script, chamando as funções internas do motor directamente. Duas correcções de forma foram necessárias (`scope_basis_refs` a apontar para ids com o prefixo `shared-understanding.md#` em vez do id nu, e `links.coverage_items` a apontar para itens que não existiam no registo por serem `not_selected`); os rascunhos errados de passagem (`coverage_v14.json`, `coverage_v17.json`) ficaram publicados e imutáveis, substituídos pelos correctos (`v15`, `v18`) — sem prejuízo, mas ficam lá.
2. A skill `aisa-render` (passo 10b) diz que o release só se constrói "num engagement com `_design/work-packages.json`" — este engagement não o tem, mas `release.py build` não o exige de facto (o ficheiro só entra na lista opcional `DESIGN`, copiado se existir). O executor correu `release.py build` mesmo assim, porque o motor não recusou e o objectivo do segmento pedia explicitamente um release; discrepância prosa-motor, não decisão de contornar uma recusa.
3. `shared-understanding.md` mantém `R-001`/`R-002` como linhas distintas de `R-003`/`R-004` (que as citam como "was") sem as marcar resolvidas — já sinalizado como possível anomalia de escrita do motor em `_coverage/coverage_v13.json#cov-023` e no `blueprint-log.md`; mesma leitura preservada nos três deliverables (nenhuma correcção feita aqui, fora do âmbito do render).
4. `discovery-report` não tem nenhuma fonte não-proibida para `solution_name` (slot obrigatório em todos os 6 templates); usado o `app.name` do registo de arquitectura ("Pedido de Equipamento Informático") para `executive-report`/`solution-blueprint` — fonte legítima para esses dois — mas para `discovery-report` isso é uma fonte proibida (bloco de arquitectura); fica `⚠️ missing: solution_name` no título, registado em `render-gaps.md` com owner `evidence`.
5. **Anomalia de protocolo (não da skill)**: este executor foi lançado como chamada única (Agent tool), que devolve um só relato final via handback, sem turno intermédio para `CONTINUA F8` — seguiu direito ao objectivo do segmento sem pausa após a retoma. Sinalizado pelo próprio executor.

Ficheiros relevantes (caminhos absolutos):
- `/home/user/aisa-refactor/projects/f8-r3-fx02/_render/f8-r3-fx02_discovery-report_v01.md`
- `/home/user/aisa-refactor/projects/f8-r3-fx02/_render/f8-r3-fx02_executive-report_v01.md`
- `/home/user/aisa-refactor/projects/f8-r3-fx02/_render/f8-r3-fx02_solution-blueprint_v01.md`
- `/home/user/aisa-refactor/projects/f8-r3-fx02/_render/render-gaps.md`
- `/home/user/aisa-refactor/projects/f8-r3-fx02/_render/render-log.md`
- `/home/user/aisa-refactor/projects/f8-r3-fx02/story.md` (Episódio 8 acrescentado)
- `/home/user/aisa-refactor/projects/f8-r3-fx02/_coverage/coverage_v15.json, _v16.json, _v18.json` (e as versões supersedidas `_v14.json`, `_v17.json`)
- `/home/user/aisa-refactor/projects/f8-r3-fx02/_release/r0001/handoff-index.json`
