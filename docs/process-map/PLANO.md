# AISA — Plano de implementação faseado: mapa de conhecimento do processo

Versão: 3.0 · Data: 25-09-2026
Estado: proposta de implementação, não implementação concluída.
Base: plano provisório fornecido pelo mantenedor e revisão nesta conversa. Os caminhos são alvos a confirmar no checkout; não se presume que números de linha, APIs ou testes da versão anterior permaneçam atuais.
Adenda v3.1 (25-09-2026) no fim deste documento: decisões do mantenedor e correcções de facto verificadas no checkout. Em conflito, a adenda prevalece. §15–§17 renumerados (o original saltava de §14 para §16).

## Roteiro de implementação — execução fase a fase

Este é um plano para implementação pelo Claude Code. A produção deste documento não autoriza nem inicia implementação. O diagnóstico anteriormente realizado serve de evidência de preparação; não constitui aceitação de M0 nem autorização de M1.

### Regras de execução e aprovação

- Executar uma fase de cada vez, na ordem M0 → M1 → M2 → M3 → M4 → M5. M6 é posterior e opcional.
- Dentro de uma fase autorizada, completar autonomamente implementação, correções e verificações necessárias. Não pedir aprovação a cada ficheiro ou teste.
- No fim de cada fase, entregar resultados concretos, alterações e demonstração; parar para revisão do mantenedor. Só iniciar a fase seguinte depois da autorização explícita correspondente.
- Aprovar o plano não aprova antecipadamente os resultados das fases. Um teste estrutural verde não equivale a aceitação funcional.
- Autoria do modelo de processo e do mapa inline. Usar revisores independentes já previstos apenas depois da versão publicada, respeitando a regra de elegibilidade. Não delegar leituras cujo detalhe alimenta a análise do autor.
- Não criar outra camada de coordenação, outro grafo ou outro sistema de coverage. Reutilizar os existentes.
- Manter mudanças locais reviewable; commits, push e merge seguem a autorização aplicável. Não mudar a versão de um piloto em curso silenciosamente.
- Falha de base conhecida fica discriminada. Nenhuma regressão nova ou teste obrigatório não executado pode ser ocultado num estado «verde».

### Entregas por fase

| Fase | Resultado utilizável | Depende de | Aprovação exige |
|---|---|---|---|
| M0 | Base e contratos de integração confirmados | Plano aceite para preparação | Matriz de consumidores, reprodução e falhas de base identificadas |
| M1 | Modelo AS-IS validável e publicável com segurança; P-0 antes da L2 | M0 aceite | Integridade, identidade, concorrência e referências demonstradas |
| M2 | Captura gera mapa visual que o dono pode rever e validar | M1 aceite | Demonstração de captura, correção e validação por revisão |
| M3 | Discovery e blueprint respondem ao processo; entrega incompleta é impedida | M2 aceite | Omissão funcional bloqueia; correção/exclusão válida resolve |
| M4 | Sessão nova recupera processo e pendências; dashboard mostra o mapa | M3 aceite | Retoma fria e mudança de fonte demonstradas |
| M5 | Primeira entrega validada num percurso completo | M4 aceite | Piloto com Excel/textos e duas omissões controladas, pacote verificável |
| M6 | Visão TO-BE separada e comparação com AS-IS | M5 aceite e autorização própria | AS-IS preservado; transformações justificadas e rastreáveis |

M1–M4 são incrementos técnicos. A primeira entrega funcional só pode ser declarada depois de M5. M6 não é requisito para fechar M5.

### M0 — Fixar base, localizar integrações e preparar a prova

**Objetivo:** o executor saber exatamente onde alterar e como distinguir comportamento existente de lacunas a resolver.

**Entrada:** este plano, checkout autorizado e acesso às fixtures do repositório. Se o SHA diferir do diagnóstico, rever apenas as conclusões afetadas; não repetir investigação sem motivo.

**Tarefas, pela ordem:**

1. Registar branch, SHA, alterações locais e instruções aplicáveis. Isolar o desenvolvimento sem apagar trabalho existente.
2. Confirmar os donos de captura, SU, decisões, cobertura, publicação, retoma e release; identificar escritores e leitores indiretos.
3. Reproduzir a enumeração de PM/CALC/linhas materiais e o caso de blueprint estruturalmente válido mas funcionalmente incompleto. Distinguir a reprodução preparada de uma descoberta semântica real.
4. Confirmar padrões de IDs e seletores. Proposta corrigida: `MAPL-001`, `MAPN-001`, `MAPE-001`, `MAPD-001`, `MAPG-001`. Não usar `MAP-D-001`: a base analisada interpreta o sufixo como decisão `D-001`.
5. Confirmar `operation.run`, validador stdlib de `workflow.py`, resolvedores de referências e APIs de coverage. Definir os contratos públicos do novo motor antes de o escrever.
6. Correr a baseline e registar falhas existentes. Resolver falhas impeditivas num ajuste isolado ou obter aceitação explícita da limitação; não normalizar uma baseline vermelha como sucesso.
7. Definir fixtures de aceitação: duas fontes com CALC de igual número, uma exceção, uma saída com consumidor, uma necessidade TO-BE nova e um requisito omitido do desenho.

**Ficheiros a produzir:** `docs/process-map/M0/RELATORIO.md`, matriz de integrações no próprio relatório, script/resultados de reprodução quando necessários. Atualizar `docs/handoff-v1/F0/consumer-matrix.json` para os novos consumidores/menções. Não criar um segundo inventário obrigatório de runtime.

**Evidência já disponível, a reconfirmar se mudar a base:** análise sobre `c97ee1c2d2052bf545f08dd8b0d07145e67c1cb3`; captura não exige P-0 antes da L2; inventário do modelo enumera PM mas não CALC/etiquetas de §4; colisão MAP-D; F06 já demonstra bloqueio de omissões conhecidas. Suite integral: 114/115 ficheiros OK, erro pré-existente em cartões F8 sem `entrega_inicial`. O relatório anterior documenta os detalhes; não é prova de aprovação desta fase.

**Critérios de fecho:** cada integração tem dono e alteração prevista; nenhuma API central é presumida; fixture reproduz o problema; falhas de base têm tratamento explícito; ausência de mapa em engagements antigos tem política definida.

**Demonstração ao mantenedor:** mostrar fonte → inventário → requisito → desenho e o ponto onde a obrigação deixa de ser representada ou é bloqueada.

**Ponto de aprovação:** aceitar base, desenho mínimo e tratamento das falhas; autorizar M1.

### M1 — Compreensão orientada e fundação do mapa

**Objetivo:** poder construir, verificar e publicar uma representação sem perder fontes, identidade ou integridade.

**Entrada:** M0 aceite; contratos de referência/publicação decididos.

**Tarefas, pela ordem:**

1. Alterar a leitura inicial da L2 para consumir `enquadramento.md` antes da interpretação. Registar P-0 ausente e discrepâncias com fontes; não descartar evidência fora do enquadramento.
2. Criar o schema `process-map/1` segundo o contrato técnico deste documento: envelope, faixas, nós, arestas, detalhes, dúvidas, órfãos, hashes e linhagem.
3. Implementar resolvedores para referências de processo e cálculos qualificadas por ficheiro. Reutilizar infraestrutura existente; acrescentar apenas os seletores em falta.
4. Implementar `check`: schema, IDs únicos, ligações, evidência, referências, retiradas e transferência de PM/PM-U/CALC/etiquetas materiais. Separar erro impeditivo de lacuna explícita.
5. Implementar `publish`: mapa corrente e snapshot histórico numa operação coordenada; precondições sobre base e fontes; recibo, repetição idempotente e recuperação. Não resolver conflito apenas incrementando versão.
6. Acrescentar `_map/` às guardas e suportar o schema nos leitores versionados. Publicação não inclui aprovação do dono nem altera estados da SU.
7. Documentar mensagens de erro e procedimento para rascunho stale. Atualizar inventário de consumidores e lista stdlib para os testes novos aplicáveis.

**Ficheiros:**

| Ação | Caminho | Alteração |
|---|---|---|
| Criar | `library/kernel/schemas/process-map.schema.json` | Contrato estrutural e versão |
| Criar | `library/kernel/tools/process_map.py` | check, publish, referências e carregamento comum |
| Alterar | `.claude/skills/aisa-capture/SKILL.md` | P-0 antes da L2; divergências preservadas |
| Alterar | `library/kernel/tools/workflow.py` | Schema suportado; reutilização do validador |
| Alterar | `.claude/hooks/pre-authority-guard.py` | Proteção de `_map/` |
| Alterar | `library/kernel/orchestration.md` | Autoridade/publicação do mapa |
| Criar | `.claude/tests/test_process_map_core.py` | Integridade, referências, publicação e recuperação |
| Atualizar | `.github/stdlib-tests.txt` e matriz de consumidores | Novos testes e consumidores reais |

`operation.py` é reutilizado. Só o alterar se uma limitação concreta impedir o contrato; justificar essa alteração separadamente no relatório.

**Testes de fecho:** MAP-03/04/05/06/09/10/11/25; primeira verificação de MAP-01/02 e linhagem MAP-12. Testar dois autores sobre a mesma base, fonte alterada entre check e publish, falha durante publicação, repetição após resposta perdida, ID retirado reutilizado e versão futura não suportada. Teste de instrução P-0 não prova execução semântica; essa prova chega no piloto.

**Demonstração:** publicar um mapa, alterar uma fonte e mostrar a recusa do rascunho antigo; repetir uma operação sem criar nova versão; mostrar que dois CALC iguais de ficheiros diferentes resolvem corretamente.

**Critérios de fecho:** nenhuma perda silenciosa de unidade enumerável; nenhuma referência inventada; histórico imutável; guardas ativas; testes dirigidos passam sem regressões novas.

**Ponto de aprovação:** rever schema, exemplos e prova de publicação; autorizar M2.

### M2 — Captura, visualização e validação pelo dono

**Objetivo:** o mapa nascer efetivamente da captura e permitir corrigir o entendimento antes do Discovery.

**Entrada:** M1 aceite; motor de publicação funcional.

**Tarefas, pela ordem:**

1. Garantir que o índice de evidência está atual antes da L2; preservar estados de extrações falhadas/incompletas.
2. Acrescentar o passo 5d de autoria inline depois da L2. Usar síntese, regras, cálculos, índice e P-0; voltar às fontes onde a síntese não chega.
3. Criar guia de autoria: agrupamento material, outputs/consumidores, exceções, dúvidas, referências e órfãos. Definir UNKNOWN com lacuna associada; nunca inventar para passar no check.
4. Implementar um único renderer SVG/HTML reutilizável, com vista tabular completa. Layout determinista; escape de rótulos; sem limite numérico que force omissões.
5. Apresentar dúvidas materiais agrupadas e pedir validação da representação. Respostas verbatim em `answers.md`, correções via nova revisão, validação externa em `decisions.md` pelo escritor existente.
6. Implementar leitura da validação: hash, revisão, âmbito, condições, responsável e timestamp. Título ou hash isolado não bastam. Mudança de conteúdo exige avaliação explícita; aprovação antiga não transita por troca de hash.
7. Integrar aviso no início de `/round`. Override justificado permite prosseguir com pendência visível; não transforma mapa incompleto em completo.

**Ficheiros:** criar `library/kernel/capture-templates/process-map.guide.md`; alterar `process_map.py`, `aisa-capture/SKILL.md`, `aisa-round/SKILL.md`, `library/kernel/phases.md` e `glossary.md`; adaptar `.claude/hooks/phase-gate-check.py` apenas na integração real do gate; criar `.claude/tests/test_process_map_capture.py` e `test_process_map_validation.py`.

**Testes de fecho:** MAP-07/15/16/24 e parte de MAP-22. Verificar texto sem Excel, Excel com extração incompleta, órfão material, correção pelo dono, validação antiga/forjada/incompleta e HTML contendo caracteres especiais. O renderer não depende de aprovação para mostrar incompletude.

**Demonstração:** captura de fixture → mapa legível → dúvida agrupada → resposta → nova revisão → validação aplicável. Abrir HTML num browser e guardar evidência visual.

**Critérios de fecho:** mapa publicado corresponde à versão mostrada; evidência e dúvidas acessíveis; nenhuma hipótese promovida a facto pela aprovação da estrutura; o dono consegue reconhecer e corrigir o processo.

**Ponto de aprovação:** aceitar experiência de revisão e formato da validação; autorizar M3.

### M3 — Discovery, blueprint e handoff ligados ao processo

**Objetivo:** impedir que uma funcionalidade material identificada desapareça entre compreensão e entrega. Esta fase faz parte da primeira entrega.

**Entrada:** M2 aceite; mapa publicável e validação consultável.

**Tarefas, pela ordem:**

1. Acrescentar `elementos` ao contrato e esqueleto SU. Definir lista de IDs, GLOBAL e N/A com razão. Linhas antigas sem coluna ficam não avaliadas; nenhuma migração silenciosa.
2. Atualizar parser e escritores/transições para preservar relações. Regra transversal pode ligar a vários elementos sem duplicar o facto.
3. Integrar IDs e caminhos `_map/` em `resolve.py`, incluindo `CITED_IDS` e `CITED_DIRS_RE`, e no read-set. Testar colisões com D/M/U e demais IDs já existentes.
4. Implementar `project`: associações, contagens por estado, referências mortas, elementos retirados e zonas sem conhecimento. Nó meramente visual sem linha SU é informação, não blocker automático.
5. Atualizar round e revisão de cobertura para percorrer o processo e tratar necessidades materiais, sem exigir uma pergunta por elemento.
6. Estender inventário e resolução de coverage para unidades materiais do mapa. Ligar essas unidades às fontes/requisitos existentes; preservar identidade das obrigações para não duplicar trabalho/estimativa.
7. Antes do blueprint, confrontar AS-IS, requisitos e decisões TO-BE. Declarar necessidade preservada, alterada, excluída ou pendente. Necessidade nova do dono entra mesmo sem origem no Excel.
8. Depois do blueprint, verificar destinos funcionais concretos: objetos/dados, ações, cálculos, automações, integrações, acessos, exceções, outputs e consumidores quando aplicáveis. Referência decorativa não é implementação funcional.
9. Propagar a cobertura atual para render e readiness do release, reaproveitando os gates existentes. Ausente, stale, inválida ou lacuna bloqueante não permitem declarar completude. Preview exploratório continua distinto de entrega pronta.
10. Empacotar mapa da revisão consumida, validação e referências essenciais; pacote autónomo não depende de caminhos locais inacessíveis.

**Ficheiros e responsabilidade:**

| Caminho | Alteração |
|---|---|
| `library/kernel/states.md`; `.claude/skills/aisa-start/SKILL.md` | Contrato e esqueleto `elementos` |
| `library/kernel/tools/dashboard.py` | Parser SU e preservação de campos |
| `library/kernel/tools/resolve.py` | Citações, read-set, escritores e preservação nas transições |
| `library/kernel/tools/process_map.py` | project e diagnóstico estrutural de associações |
| `.claude/skills/aisa-round/SKILL.md`; `.claude/agents/lens-coverage-reviewer.md` | Contexto e revisão do processo |
| `library/kernel/tools/coverage.py`; `library/kernel/coverage-contract.md` | Inventário, referências, freshness, herança e completude |
| `.claude/skills/aisa-blueprint/SKILL.md`; `.claude/skills/aisa-render/SKILL.md` | Leitura e verificação nos pontos de produção |
| `library/kernel/tools/functional.py`, `trace.py`, `release.py` | Ligar apenas os gates necessários; preservar autoridades existentes |
| `library/kernel/handoff-contract.md` | Conteúdo e referências do pacote |
| `.claude/tests/test_process_map_coverage.py` | Omissões, correção, exclusão e propagação até release |

**Testes de fecho:** MAP-07/08/12/13/14/17/18/20/21/22/27. Cobrir as três variantes de MAP-21 separadamente, com o resto do pacote válido, para provar qual condição bloqueou. Confirmar que uma obrigação partilhada por dois elementos não duplica esforço.

**Demonstração obrigatória:** retirar do blueprint uma funcionalidade existente no mapa mantendo YAML válido → gate bloqueia com fonte e destino em falta → corrigir → passa. Num ramo separado, excluir legitimamente com decisão e verificar âmbito parcial. Repetir sem autoridade de exclusão e confirmar recusa.

**Critérios de fecho:** omissão funcional chega ao gate final; correção efetiva fecha o achado; exclusão não autorizada falha; desenho aprovado sobre premissas antigas não é reutilizado como atual; entregáveis não inventam o comportamento perdido.

**Ponto de aprovação:** mantenedor verifica a demonstração negativa e positiva; autorizar M4. Suite verde sem esta demonstração não fecha M3.

### M4 — Contexto, retoma e observabilidade

**Objetivo:** recuperar o processo numa sessão nova e voltar ao detalhe certo em cada fase.

**Entrada:** M3 aceite; relações e coverage operacionais.

**Tarefas, pela ordem:**

1. Implementar `summary` com revisão/hash, validação, freshness, bloqueios, estado por bloco e referências para expansão.
2. Integrar mapa nos inputs de `bootstrap` e na leitura consistente. Resumo deve corresponder aos mesmos bytes do snapshot, sem leitura posterior não verificada.
3. Contabilizar mapa no orçamento existente. Declarar contexto parcial e material não carregado; não colocar nós no grafo para contornar limites.
4. Atualizar a retoma real em `workflow.py`, `aisa-status` e comando `/resume`. Recuperar também decisões posteriores, trabalho interrompido e bloqueios antes de propor ação.
5. Explicitar checkpoints: visão global no Framing; cálculos/volumes/exceções relevantes em Options; jornada completa em blueprint/FC; comportamento autorizado em trabalho/estimativa; destinos e pendências no handoff.
6. Adicionar separador Mapa ao dashboard usando o renderer existente. Invalidar a vista por mudanças em mapa, SU, validação e coverage consumido; regenerar explicitamente após publicação, sem depender apenas de hooks de edição.
7. Testar fonte alterada entre sessões e revalidação proporcional. Nenhum «hash atualizado» sozinho permite regressar a atual.

**Ficheiros:** `process_map.py`, `bootstrap.py`, `workflow.py`, `dashboard.py`; `.claude/skills/aisa-status/SKILL.md`, `aisa-frame/SKILL.md`, `aisa-options/SKILL.md`; `.claude/commands/resume.md`; `.claude/hooks/on-su-change.py`; ajustes mínimos nas skills de blueprint/render já alteradas; `.claude/tests/test_process_map_resume.py` e testes de linguagem aplicáveis.

**Testes de fecho:** MAP-23/24 e freshness MAP-22; consumo dentro de revisão consistente; orçamento excedido; SU antiga; mapa ausente; fonte alterada; recuperação pendente; HTML estável com inputs iguais.

**Demonstração:** fechar sessão, abrir outra sem histórico, executar `/resume` e identificar processo, âmbito, alterações, lacunas e próxima ação a partir dos ficheiros. Alterar uma fonte e repetir: o estado antigo deve aparecer por revalidar.

**Critérios de fecho:** reconstrução sem conversa anterior; incompletude explícita; dashboard consistente com motores; checkpoints pedem detalhe quando material sem recarregar sempre todos os Excel.

**Ponto de aprovação:** aceitar retoma e apresentação; autorizar M5.

### M5 — Piloto integral e aceitação da primeira entrega

**Objetivo:** demonstrar utilidade funcional e persistência, além de checks estruturais.

**Entrada:** M4 aceite; caso representativo autorizado com Excel e textos. Dados do utilizador só entram com acesso/âmbito autorizado; fixture sintética permite demonstração técnica, mas não substitui a avaliação de compreensão de um processo real.

**Tarefas, pela ordem:**

1. Fixar SHA, fontes, perfil/âmbito e expectativas de avaliação. Separar referências esperadas do contexto do autor para não fornecer a resposta ao piloto.
2. Executar captura e autoria inline, registar limitações, apresentar mapa ao dono e incorporar correções sem reclassificação automática de hipóteses.
3. Executar Discovery, Framing, Options e decisão no percurso aplicável. Verificar que novos requisitos do dono entram mesmo sem origem no AS-IS.
4. Em cópia controlada, omitir uma necessidade da compreensão L2/mapa e avaliar revisão das fontes/dono: MAP-19. Registar quem descobriu, com que evidência e como corrigiu a montante. Não simular descoberta por inserir manualmente um achado e anunciá-lo como automático.
5. Noutro ramo, omitir uma funcionalidade do desenho: MAP-17. Mostrar bloqueio e fecho após correção; manter evidência da execução falhada.
6. Efetuar retoma fria antes do handoff; produzir especificação e estimativa calculada a partir do trabalho autorizado.
7. Verificar pacote fora da pasta original, incluindo referências, âmbito, exclusões, cobertura e limitações. Não declarar solução Power Platform implementada: esta entrega valida o framework de pré-desenvolvimento/handoff.
8. Executar suite integral e subset stdlib aplicável. Quando se afirmar runtime stdlib, demonstrá-lo em ambiente apropriado sem dependências opcionais; listar skips/not-run e falhas conhecidas.
9. Rever instruções e exemplos para não prometer completude sem evidência. Entregar relatório com limitações residuais e retoma operacional.

**Ficheiros:** fixture sob `.claude/tests/fixtures/` e registos de piloto no local de evidência definido em M0; `docs/process-map/M5/RELATORIO.md`; atualizar registos de fixtures/consumidores aplicáveis, documentação operacional e testes apenas para regressões concretas descobertas.

**Testes de fecho:** rever MAP-01 a MAP-25 e MAP-27; MAP-26 pertence a M6. MAP-01/02/19 exigem evidência da execução semântica; os restantes exigem a combinação de checks automatizados e demonstração indicada nas fases.

**Critérios de aceitação da entrega:** todas as necessidades materiais do âmbito têm destino funcional ou pendência impeditiva; nenhuma exclusão sem autoridade; omissão no desenho bloqueia; dúvida não desaparece na retoma; pacote verificável; estimativa corresponde ao trabalho autorizado. Nenhuma limitação de extração/compreensão é ocultada.

**Ponto de aprovação:** aceitar a primeira entrega ou devolver achados às fases responsáveis. Só depois decidir adoção e eventual M6. Não usar aprovação de M5 como autorização automática de publicação externa.

### M6 — TO-BE visual, evolução posterior

**Objetivo:** mostrar transformação do processo sem apagar a referência original.

**Entrada:** M5 aceite e necessidade concreta desta capacidade, com autorização própria.

**Tarefas:** acrescentar `_map/to-be.json` e histórico próprio; ligar ao AS-IS e decisões; representar preservado/alterado/eliminado/novo; suportar divisões/fusões e comparação visual; manter cobertura e obrigações da primeira entrega sem duplicação; atualizar summary/dashboard apenas onde necessário.

**Ficheiros:** schema e `process_map.py`, suporte de versões em `workflow.py`, vistas em `dashboard.py`, instruções pós-decide e testes TO-BE. Identificar a skill exata em M0/M6 antes de editar; não converter automaticamente a perspetiva de `_map/map.json`.

**Testes/fecho:** MAP-26, regressão da linhagem MAP-12 e da cobertura MAP-17/21. AS-IS continua acessível; cada transformação material tem decisão; novo requisito não recebe falsa origem no Excel.

**Demonstração/aprovação:** comparar duas jornadas AS-IS/TO-BE e navegar até às decisões e cobertura. Fechar apenas após revisão do mantenedor.

### Protocolo de fecho e retoma de cada fase

Um único relatório por fase, sem criar nova máquina de estados no runtime. O relatório contém:

```markdown
# M<n> — <nome>
Estado: em curso | pronto para revisão | aceite | bloqueado
Base: <branch e SHA>
Resultado: <capacidade que passou a funcionar>
Alterações: <ficheiros e comportamento>
Verificação: <comandos; resultados; skips; not-run>
Demonstração: <inputs; falha observada; correção; evidência>
Limitações: <abertas e impacto>
Decisão do mantenedor: <pendente ou referência à autorização real>
Retoma: <próxima ação exata e pré-condições>
```

«Pronto para revisão» é conclusão do executor; «aceite» requer decisão real do mantenedor. Na mudança de sessão, ler este plano, o último relatório e o estado do checkout. Revalidar a base antes de continuar; não pedir ao utilizador que reconte toda a conversa.

### Prompt de arranque para Claude Code

```text
Lê este plano de implementação faseado e as instruções do repositório.
A implementação corre no Claude Code. Começa apenas pela fase que eu autorizar.
Dentro dessa fase, implementa e verifica até todos os critérios de fecho estarem
satisfeitos ou existir um bloqueio concreto que não possas resolver no âmbito.
Reutiliza o diagnóstico anterior se a revisão ainda for aplicável; não confundas
esse diagnóstico com aprovação da fase. Não alteres engagements ou pilotos em curso.
Mantém a autoria do process-model e do mapa inline; respeita a regra de delegação.
No fim entrega o relatório, as alterações e a demonstração pedida, e aguarda a
minha aprovação antes de iniciar a fase seguinte. Não declares completude só por
suite verde, referências presentes ou HTML gerado. Não adies blueprint/coverage e
release para a fase TO-BE. Não faças push ou merge sem autorização aplicável.
```

## Contrato técnico e matriz de aceitação

As secções seguintes detalham o que implementar. O roteiro acima define quando, em que ficheiros, com que provas e em que ponto parar para aprovação.

## 1. Problema e objetivo

Foi observado pelo mantenedor um blueprint com objetos e funcionalidades esperados em falta. A localização exata da perda ainda tem de ser demonstrada: captura incompleta, transferência incompleta para requisitos, exclusão indevida ou autoria incompleta do desenho. Não tratar uma dessas hipóteses como causa já provada.

O objetivo é tornar o processo compreendido uma referência persistente que acompanha o engagement desde a captura até ao handoff. A nova capacidade deve permitir responder: que necessidades materiais foram identificadas, onde estão fundamentadas, como foram tratadas e onde se concretizam na solução?

O mapa tem dois níveis:
- Nível 0: processo legível, com intervenientes, passos, decisões, exceções, saídas e consumidores.
- Nível 1: referências por bloco ou ligação a dados, cálculos, regras, workflows e outputs relevantes.

A primeira entrega só está completa quando a omissão de uma funcionalidade material do mapa é detetada na revisão do blueprint. Um diagrama, por si só, não satisfaz este objetivo.

## 2. Princípios e fronteiras

1. Ficheiros e declarações do dono fornecem evidência; o dono valida e corrige a representação.
2. O enquadramento P-0 orienta a compreensão antes da L2. Evidência fora dele ou que o contradiga permanece visível.
3. Extração determinística, compreensão semântica, representação do processo e aprovação são atividades distintas.
4. A autoria da L2 e do mapa corre inline. Escrever num ficheiro não torna a autoria elegível para subagente. Revisão independente só depois de existir uma versão, segundo a regra central de delegação.
5. SU é autoridade dos factos, pressupostos, riscos, conflitos e questões. Decisões autorizam âmbito e transformações. Blueprint e FC são autoridades da solução e do comportamento TO-BE.
6. O mapa organiza conhecimento e referências. Não se torna outra base factual nem outro workflow de decisões.
7. Publicação usa o coordenador existente, com read-set, conflitos, receipts e recuperação. Não criar outro motor transacional.
8. Coverage existente é o dono da cobertura. O mapa acrescenta unidades e ligações; não cria um sistema paralelo de aprovação de completude.
9. Preservar o AS-IS. Uma decisão TO-BE não reescreve a história do processo.
10. Reutilizar avaliações atuais; reavaliar dependências alteradas. Hash diferente exige avaliação, não prova automaticamente mudança semântica nem autoriza classificá-la como editorial.
11. Não contornar guardas de escrita por outro editor, Bash ou variável de ambiente. Alterações ao framework seguem o procedimento autorizado de desenvolvimento; em execução do engagement, library continua protegida.

## 3. Âmbito e primeira entrega

### Incluído na primeira entrega

- P-0 consumido pela L2, sem alterar a natureza determinística da extração.
- Modelo estruturado AS-IS, publicação versionada e render determinista.
- Validação da representação pelo dono, com dúvidas explícitas.
- Relações SU ↔ mapa, incluindo múltiplos elementos e conhecimento transversal.
- Integração nas etapas existentes de reconciliation, blueprint e render.
- Gate de completude que chega à avaliação do release.
- Retoma por referências e leitura dirigida, com orçamento explícito.
- Evidência ponta a ponta que reproduz omissões no mapa e no desenho.

### Adiado

- Edição visual por drag-and-drop, BPMN completo ou modelador genérico.
- Inferência automática de tabelas Dataverse/ecrãs a partir de folhas Excel.
- Grafo independente e nova plataforma de agentes.
- Modelo TO-BE visual completo e comparação visual avançada entre versões.

Adiar o mapa TO-BE completo não adia a obrigação de indicar, na cobertura da primeira entrega, o destino de cada necessidade material: preservada, alterada, excluída ou pendente. Necessidades TO-BE novas são registadas em SU/decisões e entram na cobertura mesmo sem origem no AS-IS.

## 4. Autoridades e ficheiros

| Conteúdo | Dono | Papel do mapa |
|---|---|---|
| Evidência original | inputs e declarações registadas | Referencia |
| Extrações e modelo de compreensão | _capture | Referencia com versão/hash |
| Factos e questões | SU; respostas verbatim em answers.md | Organiza por elementos |
| Âmbito, validações e alterações autorizadas | decisions.md | Aponta para os atos aplicáveis |
| Estrutura AS-IS | mapa AS-IS versionado | Autoridade da representação |
| Comportamento futuro | FC autorizados | Liga através de requisitos/coverage |
| Arquitetura | blueprint aprovado | Liga através de coverage |
| Destino/cobertura material | registos de coverage | Projeta resultados |
| Trabalho e esforço | inventário/spec e estimate | Não duplica |

Caminhos propostos para a primeira entrega:
- `_map/map.json`: revisão AS-IS corrente, publicada pelo coordenador.
- `_map/history/mp-vNN.json`: snapshots imutáveis.
- `process-map.html`: vista derivada; nunca fonte de verdade.

Na introdução do TO-BE, preservar `_map/map.json` como referência AS-IS para compatibilidade e acrescentar `_map/to-be.json`, com histórico próprio e referência explícita ao AS-IS. A perspetiva é imutável por linha de versões; nunca mudar o ficheiro AS-IS para `perspective: to_be`.

## 5. Modelo mínimo proposto

Novo `library/kernel/schemas/process-map.schema.json`, versão `process-map/1`. Seguir o validador e convenções existentes, sem nova dependência de runtime.

### 5.1 Envelope

- `schema_version`, `engagement_id`, `version` (`mp-vNN`), `perspective`.
- `based_on`: referências aos inputs efetivamente consumidos, com SHA e revisão quando disponível. Inclui enquadramento, modelo de processo, extrações, replay e textos usados.
- `sources`: inventário/disposições por fonte, preferencialmente por referência ao registo existente; não criar outra cópia de evidência.
- `lanes`, `nodes`, `edges`, `details`, `gaps`, `orphans`, `retired_ids`.

Não fazer um schema aberto descartar campos desconhecidos. Reutilizar a política existente de preservação e diagnóstico de versões não suportadas.

### 5.2 Elementos

| Coleção | Campos mínimos |
|---|---|
| lanes | id, label, kind: actor/tool/channel/consumer/downstream |
| nodes | id, kind: trigger/step/decision/exception/output, label, lane, order, marker, evidence; sla opcional |
| edges | id, src, dst, kind: normal/exception/branch, label opcional, carries (lista de refs), marker, evidence |
| details | id, attaches_to (lista não vazia), kind: workflow/table/column/calculation/intermediate/output/rule, label, ref, marker |
| gaps | id, attaches_to (lista ou âmbito global explícito), question, respondent opcional, pm_u_ref opcional |
| orphans | ref, reason: gap_in_map/out_of_scope/undetermined, note; decision_ref quando necessário |

Markers: OBSERVED/INFERRED/HYPOTHESIS/UNKNOWN, com o significado já usado na captura. Não são os estados epistémicos da SU.

Regras de evidência:
- Nodes e edges com afirmações não UNKNOWN levam evidence resolúvel. INFERRED/HYPOTHESIS levam a base da inferência; isso não os torna observados.
- Em details, `ref` é a referência de evidência e satisfaz a exigência; não exigir também um campo duplicado `evidence`.
- Lanes são agrupamentos; não exigir uma prova própria redundante para cada faixa. Afirmações de responsabilidade são fundamentadas nos passos/regras associados.
- UNKNOWN pode não ter evidência, mas tem lacuna associada. Nunca inventar uma referência para passar no check.
- Gaps/orphans têm referências e estrutura específicas, não são sujeitos cegamente à mesma regra dos nodes.

### 5.3 Identidade e referências

Usar prefixos propostos `MAPL-`, `MAPN-`, `MAPE-`, `MAPD-`, `MAPG-`, confirmando os leitores em M0. O diagnóstico na base c97ee1c demonstrou colisão de `MAP-D-001` com a decisão `D-001`. IDs persistem entre versões e nunca são reutilizados após retirada.

Referências a captura devem ter caminho e âncora, por exemplo `_capture/<workbook>.calc-chain.json#CALC-003`. O seletor exato deve ser suportado pelo resolvedor real, ou receber um adaptador mínimo com teste. `CALC-003` isolado não identifica uma fonte num engagement com vários Excel.

Histórico estrutural existe desde o início:
- `was`: lista de IDs predecessores em divisões, fusões ou substituições.
- `retired_ids`: preserva IDs retirados; a versão anterior contém o conteúdo histórico.
- Novo elemento que substitui outro identifica a relação. Uma exclusão sem sucessor fica explícita e justificada.
- Uma linha SU que aponta para um elemento retirado fica sinalizada; não é reapontada automaticamente para todos os sucessores.

## 6. Motor e publicação

Novo `library/kernel/tools/process_map.py`, stdlib, reutilizando coordenação, resolução, validação e hashes existentes.

| Comando | Responsabilidade |
|---|---|
| check --engagement <slug> --draft <f> | Schema, integridade, referências, inventário e lacunas |
| publish --engagement <slug> --draft <f> | Publicação coordenada, histórico e idempotência |
| render --engagement <slug> | HTML/SVG determinista a partir da revisão publicada |
| project --engagement <slug> | Ligações à SU e cobertura existente, sem escrever factos |
| summary --engagement <slug> --json | Contexto compacto e referências para expansão |

O rascunho fica fora das autoridades correntes. A publicação testa a revisão base do mapa e todo o read-set consumido. Se mudarem, recusa com o código estruturado já usado no repositório para inputs stale; não introduzir BASE_CHANGED como sinónimo sem necessidade.

Não basta incrementar mp-vNN para resolver conflito: reabrir sobre a base atual, reconciliar o conteúdo e avaliar as diferenças. Revisões antigas nunca são sobrescritas. O receipt permite repetir uma operação sem criar outra versão.

O check separa:
- Erro estrutural/referência inválida: impede publicação.
- Lacuna semântica explícita: pode publicar como mapa incompleto e deve continuar visível.
- Erro inesperado na avaliação: resultado não verificado, nunca sucesso silencioso.

Uma alteração de dependência exige revalidação registada segundo o mecanismo existente. Atualizar hashes sem avaliação não torna o mapa atual. Alterações estruturais ou semânticas materiais invalidam a validação aplicável; alterações de apresentação não devem obrigar a nova decisão de negócio. O ato que valida uma revisão antiga nunca passa a validar automaticamente outra.

## 7. Captura: orientar antes de interpretar

### Antes da L2

Atualizar `aisa-capture` para ler P-0 (`enquadramento.md`) e contexto antes da compreensão cross-source. Interpretar T1–T4 conforme o formato realmente existente: atores, gatilho, atividades, resultados/consumidores.

P-0 é uma hipótese/enquadramento declarado, não um filtro de exclusão. Registar diferenças entre o que o dono descreveu e o que os ficheiros revelam. Se não existir, declarar enquadramento indisponível e preservar os limites, sem inventá-lo.

### Execução

1. L1/L3 por workbook e LT por texto: produzir evidência normalizada.
2. Garantir que o índice de evidência corresponde aos resultados atuais antes de a L2 o ler. Ajustar a ordem existente se o índice só for reconstruído depois.
3. L2 inline: reconstruir processo cruzando fontes e P-0, mantendo regras, hipóteses e dúvidas citadas.
4. Passo 5d inline: criar o mapa a partir dessa compreensão e fontes necessárias, executar check, publicar e renderizar.
5. Apresentar representação, lacunas e validação pendente.

Execuções determinísticas podem correr em paralelo quando independentes. Evitar escritas concorrentes no índice/log partilhado: coordenar essas escritas ou usar o mecanismo seguro já existente. Não lançar a L2 enquanto os inputs de que depende ainda estão em produção. Falhas/indisponibilidades são registadas segundo a política existente de degradação.

### Profundidade

Nível 0 orientado a compreensão; nível 1 guarda referências e agrupamentos. Sem um elemento por célula. Não impor um limite de nós que force omissões: quando o diagrama ficar denso, agrupar visualmente e permitir expansão, mantendo todos os elementos e arestas no modelo e tabela.

## 8. Cobertura: quatro perguntas diferentes

| Camada | Pergunta | Evidência |
|---|---|---|
| Leitura das fontes | Foram examinadas as fontes/unidades relevantes? | Inventário, disposições e locators |
| Transferência da compreensão | Cada PM/CALC/PM-U e linha material tem destino? | Elemento do mapa ou órfão explícito |
| Validação funcional | A representação corresponde ao processo e ao âmbito reconhecido? | Revisão do dono e dúvidas preservadas |
| Concretização | A solução responde às necessidades materiais? | Requisitos → blueprint/FC → trabalho → aceitação |

O denominador não pode depender só das linhas que a L2 decidiu escrever. Reutilizar o inventário de fontes de coverage para identificar unidades ainda não examinadas e confrontar outputs/consumidores do P-0 com a compreensão obtida. Julgamento semântico continua necessário; um regex não prova que todo o negócio foi compreendido.

A regra mecânica de transferência conta PM, CALC, PM-U e etiquetas materiais de §4 através de referências resolvidas. Uma referência pode cobrir um grupo declarado, nos termos atuais de coverage, sem criar milhares de nós.

Órfão não equivale a cobertura:
- gap_in_map: trabalho pendente de representação/compreensão.
- undetermined: materialidade/destino por avaliar.
- out_of_scope: justificação; decisão autorizada quando exclui necessidade material do âmbito.

Órfãos materiais ou de materialidade indeterminada não podem desaparecer da avaliação final. Prosseguir exploratoriamente com override não os transforma em completos.

## 9. Validação pelo dono

Usar perguntas agrupadas por tema/jornada. Priorizar dúvidas que alterem a estrutura, o âmbito ou a próxima tarefa; não fazer uma pergunta por cada célula/gap. Um mapa pode ter a sua representação validada com dúvidas documentadas.

Persistir respostas verbatim em answers.md pelo escritor existente. Correções factuais seguem o fluxo normal para SU; o mapa é atualizado com referências a essa evidência, sem promoção automática de markers.

Bloco proposto em decisions.md, publicado por draft/publish:

```markdown
## D-NNN — Mapa do processo mp-vNN validado
- **Map sha256**: <hash da revisão>
- **Scope**: <âmbito validado>
- **Conditions**: <limitações e dúvidas mantidas, ou nenhuma>
- **Validated by**: owner (<papel>, via AskUserQuestion)
- **Timestamp**: <ISO>
```

O leitor valida campos, papel, hash e revisão; a existência do título não basta. Reutilizar as validações de atos humanos já corrigidas no projeto. Render/project consultam o ato externo; não alterar o mapa para lhe inserir a sua aprovação e criar um ciclo de hashes.

Em /round, mapa ausente, stale ou sem validação aplicável gera aviso e pedido de override justificado. O portão suave permite continuar a análise, mas a pendência acompanha blueprint e handoff. Nunca apresentar como validado pelo dono um mapa apenas publicado pelo agente.

## 10. Discovery e ligações à SU

Adicionar a coluna `elementos` no fim das secções, preservando compatibilidade de leitores. Aceitar várias referências de mapa numa linha; definir representação global explícita e N/A com razão. Confirmar delimitador compatível com tabelas Markdown e testar escape/parser.

- Linhas antigas sem coluna: estado de associação não avaliado; nunca cobertura implícita nem migração silenciosa.
- Linhas novas: uma ou várias referências, GLOBAL ou N/A justificado.
- Conhecimento transversal não precisa de ser artificialmente duplicado por cada nó.
- A referência organiza a linha; não muda estado, evidência ou autoridade da SU.

Atualizar parser, escritores, schemas/templates pertinentes e CITED_IDS/resolvedor. Referência ao mapa entra no read-set.

O summary entra no round. O analista usa-o para percorrer o processo, identificar desconhecidos e confrontar as seis perspetivas. O revisor de cobertura recebe a revisão do mapa e os registos de coverage.

Project devolve: contagem epistémica por elemento; elementos sem associações; linhas sem associação avaliada; referências mortas; elementos retirados que exigem avaliação de reapontamento. Elemento sem linha é sinal, não blocker automático: um conector visual pode dispensar uma afirmação própria. Completude depende das necessidades e obrigações materiais, não de atingir uma contagem mínima de linhas.

## 11. Blueprint, render e release — incluídos já

### Antes do blueprint

Estender reconciliation com unidades do mapa e referências às unidades originais, evitando duplicar obrigações já identificadas pelos mesmos requisitos. Preservar a relação entre unidade de mapa e evidência original.

O autor lê: visão global do mapa, decisões posteriores e detalhe das jornadas no âmbito. Compara necessidades AS-IS com requisitos TO-BE já autorizados e regista o destino de cada necessidade material usando os campos/disposições atuais de coverage, estendendo-os apenas se necessário.

Destinos funcionais:
- Preservada: aponta para requisito e comportamento futuro.
- Alterada: requisito/comportamento futuro e decisão que justifica a alteração.
- Excluída: razão e autoridade correspondente.
- Pendente: lacuna com responsável e impacto; não é covered.

Requisitos novos TO-BE entram independentemente de haver um nó AS-IS. Não exigir invenção de evidência no Excel para uma necessidade declarada pelo dono.

### Depois do blueprint

A revisão existente verifica as obrigações herdadas contra a versão concreta: dados, FC, aplicações/superfícies, automações, integrações, permissões, exceções e outputs quando aplicáveis. Reutilizar a revisão disponível; não criar automaticamente outro agente.

Uma necessidade material omitida ou parcialmente representada retorna como achado com origem e responsável. Pode existir preview, mas não estado de desenho completo nem nova aprovação que dependa dessa completude enquanto houver lacuna bloqueante. A política de âmbito parcial exige exclusões autorizadas e dependências coerentes.

### Render e release

Render continua a projetar autoridades. Não reabre o Excel para inventar comportamento em falta. Lacunas regressam ao autor adequado.

O gate final deve consumir a cobertura atual aplicável desde a reconciliação até ao render. Registo ausente, inválido, stale ou incompleto não pode converter-se em ready. Se a implementação já faz esta propagação, reutilizá-la; se não, ligar os leitores necessários e provar ponta a ponta.

Antes do handoff, a revisão existente recebe um mapa compacto do âmbito e o tratamento de cada necessidade material. Verifica omissões, não refaz toda a captura. O destinatário independente pode receber o mapa como parte do pacote, identificado como AS-IS e acompanhado das decisões TO-BE, sem histórico de raciocínio do autor.

O release inclui a revisão do mapa efetivamente usada, a validação pertinente e as referências/artefactos de cobertura necessários para interpretar o pacote. Referências que só funcionem no engagement original devem ser materializadas no pacote ou declaradas como dependência externa; um pacote anunciado como autónomo não pode depender de ficheiros locais ausentes.

## 12. Contexto, mudanças e retoma

| Momento | Contexto mínimo |
|---|---|
| Framing | Objetivo, atores, etapas, outputs/consumidores, lacunas de âmbito |
| Options | Restrições, volumes, cálculos, integrações, exceções materiais às alternativas |
| Blueprint/FC | Detalhe por jornada e fontes necessárias à especificação |
| Inventário/estimate | Comportamento autorizado, diferenças e obrigações de construção/teste/operação |
| Handoff | Mapa compacto, destinos, exclusões, bloqueios e cobertura da versão |

Bootstrap regista o mapa e dependências consumidas no input_revision. Summary usa o orçamento existente e devolve versão, validação, freshness, situação global, bloqueios e referências para expansão. Inclui partial=true e o que ficou por carregar quando não cabe. Se nem os bloqueios materiais couberem, devolve estado parcial explícito e pede divisão/expansão; nunca omite silenciosamente.

Não adicionar os elementos ao grafo só para contornar um limite, nem declarar o summary fora do orçamento. Na sessão nova, reavaliar hashes e recuperar decisões posteriores ao mapa antes de agir.

Quando houver nova fonte, resposta ou alteração de âmbito: analisar impacto sobre L2/mapa/cobertura e derivados. Reutilizar unidades comprovadamente não afetadas. Alteração editorial exige avaliação registada, sem reabrir automaticamente decisões materiais. Conhecimento do pack não consumido não desencadeia revisão por defeito.

## 13. Render e dashboard

Layout SVG por lane/order com ordenação estável por ID como desempate. Evidenciar branches, exceções, outputs/consumidores e elementos por esclarecer. Escape de todos os rótulos/atributos; não executar HTML vindo das fontes.

O mesmo mapa produz vista autónoma e separador Mapa no dashboard. Evitar duplicar dois renderers e não obrigar a introduzir uma biblioteca externa de layout. Vista tabular completa serve de alternativa quando as arestas cruzadas reduzem legibilidade.

Determinismo: mesmos inputs semânticos e mesmo estado projetado produzem os mesmos bytes. Não inserir relógio atual ou IDs aleatórios no HTML. Se a vista inclui SU/validações, estes também fazem parte dos inputs da verificação de determinismo.

Invalidar/regenerar a vista quando mudam mapa, SU, atos de validação ou coverage consumido. Confirmar o evento real dos hooks: não presumir que on-su-change observa escritas em _map. Não editar HTML derivado para corrigir conhecimento.

## 14. Ficheiros e integrações a confirmar

| Grupo | Alvos |
|---|---|
| Novos | schemas/process-map.schema.json; tools/process_map.py; capture-templates/process-map.guide.md; testes dirigidos |
| Captura/análise | aisa-start; aisa-capture; aisa-round; aisa-frame; aisa-options; lens-coverage-reviewer |
| Desenho/entrega | aisa-blueprint; aisa-render; leitores de revisão relevantes; contrato de handoff |
| Persistência | bootstrap.py; resolve.py; workflow.py; leitores de versões suportadas |
| Coverage/gates | coverage.py e coverage-contract.md; functional/trace/release quando necessários à propagação |
| Observabilidade | dashboard.py; aisa-status; .claude/commands/resume.md; hooks efetivamente ligados à publicação |
| Contratos | states.md; templates SU; phases.md; glossary.md; orchestration.md; documentação de operação |
| Proteções | pre-authority-guard; inventário de caminhos coordenados; regras de publicação |
| Testes | stdlib-tests.txt e matrizes de consumidores relevantes |

M0 deste plano resolve os caminhos completos, enumera leitores/escritores e identifica a menor alteração por alvo. Não adicionar comandos, estados ou ficheiros onde já exista um dono equivalente.

## 15. Matriz de testes de aceitação

| ID | Cenário | Resultado esperado |
|---|---|---|
| MAP-01 | L2 com P-0 disponível | Instrução e execução registam consumo antes da interpretação |
| MAP-02 | Fonte contradiz P-0 ou mostra outro output | Diferença visível; não descartada por falta de encaixe |
| MAP-03 | Lane/src/dst/attaches_to inexistente | Publicação recusada com erro localizado |
| MAP-04 | Nó observado sem fonte; detail com ref válido | Primeiro recusado; segundo aceite sem campo evidence redundante |
| MAP-05 | Dois Excel com CALC-003 | Referências resolvem separadamente por ficheiro |
| MAP-06 | PM/CALC/PM-U/etiqueta material sem destino | Transferência incompleta identificada |
| MAP-07 | Elemento material enviado para orphan undetermined | Pode persistir incompleto; não conta como covered nem permite falso ready |
| MAP-08 | Exclusão material sem autoridade | Gate final recusa; decisão válida e coerente permite parcial |
| MAP-09 | Repetição de publicação após perda de resposta | Mesmo receipt/efeito; sem nova versão indevida |
| MAP-10 | Crash e dois escritores na mesma base | Antiga/nova revisão consistente ou recuperação exigida; conflito explícito |
| MAP-11 | Fonte muda durante autoria/publicação | Recusa stale; rascunho preservado |
| MAP-12 | Dividir/fundir/retirar elemento | Histórico/IDs preservados; SU sinalizada para reapontamento |
| MAP-13 | Linha associada a dois passos; regra global; SU antiga | Leitura correta; nenhum vínculo inventado para a antiga |
| MAP-14 | Trigger visual sem linha SU | Sinal informativo; não cria blocker artificial |
| MAP-15 | Validação com hash antigo/campos ausentes | Não reconhecida como validação atual |
| MAP-16 | Dono valida estrutura com hipótese aberta | Hipótese mantém estado e lacuna continua visível |
| MAP-17 | Funcionalidade no mapa e ausente do blueprint | Achado com fonte; desenho/entrega não anunciados completos |
| MAP-18 | Mesma funcionalidade corrigida ou excluída legitimamente | Gate passa só no âmbito e versão correspondentes |
| MAP-19 | Funcionalidade omitida da própria L2/mapa | Revisão de fonte/dono identifica a perda; não fingir deteção semântica por regex |
| MAP-20 | Requisito TO-BE novo sem origem no Excel | Admitido por evidência/decisão do dono; entra em cobertura |
| MAP-21 | Coverage ausente/stale/inválida com resto do pacote válido | Ready recusado com razão aplicável |
| MAP-22 | Alteração editorial e alteração material | Revalidação explícita proporcional; hash swap sozinho não fecha |
| MAP-23 | Retoma sem conversa; contexto não cabe | Recupera referências/bloqueios ou declara parcial e expande |
| MAP-24 | Mesmo input; rótulo contém HTML/script | Render idêntico e escapado; nenhum código da fonte executado |
| MAP-25 | Escrita direta em estado coordenado | Guarda recusa nos caminhos cobertos; limites de hooks documentados |
| MAP-26 | Novo TO-BE | Referência AS-IS e linhagem preservadas |
| MAP-27 | Pacote revisto fora do engagement | Referências essenciais acessíveis; não depende de caminhos privados ausentes |

MAP-01 (execução semântica), MAP-02 e MAP-19 requerem avaliação documentada do comportamento da sessão, além dos testes estruturais. Fixture pré-escrita não prova que o agente descobriu a necessidade.

Executar testes dirigidos durante cada incremento e regressões relevantes. Na entrega, suite completa aplicável e subset stdlib; registar contagens reais, skips, falhas esperadas e not-run. Não fixar contagens previstas como critério de sucesso.

No piloto: renderizar HTML num browser e verificar faixas, decisões, exceções, tabela, expansão e legibilidade; guardar screenshot como evidência complementar. A imagem não prova cobertura semântica.

## 16. Piloto mínimo e critério de fecho

Escolher caso com pelo menos uma cadeia de cálculo, exceção, intervenção humana, objeto de negócio e output consumido por outra pessoa/sistema. Pode ser sintético para testes; complementar com um caso representativo autorizado para avaliar compreensão real.

Procedimento:
1. Fixar código, inputs e expectativas de avaliação, sem fornecer respostas esperadas ao autor/revisor independente.
2. Capturar, compreender com P-0 e produzir mapa inline.
3. Dono revê estrutura/âmbito; registar correções e dúvidas.
4. Executar Discovery e desenho com mapa/requisitos/decisões.
5. Injetar separadamente omissão na compreensão e omissão no blueprint. Guardar a execução falhada.
6. Confirmar deteção pela camada adequada e correção a montante.
7. Retomar numa sessão sem conversa anterior.
8. Produzir e rever pacote completo do âmbito, incluindo especificação e estimativa realmente calculada quando aplicáveis.

Fecho: todos os elementos materiais do âmbito têm destino rastreável ou pendência explícita que impede declarar completude; não há exclusões materiais sem autoridade; blueprint incompleto não passa por completo; retoma preserva o conhecimento e as decisões. Sem piloto real de compreensão, declarar apenas mecanismos demonstrados sobre fixtures. Implementação efetiva em Power Platform continua uma prova distinta.

## 17. Rollback e operação

Manter versões antigas e drafts recuperáveis. Não remover mapa/coluna da SU por downgrade. Se um leitor anterior não suporta os novos campos, usar leitor compatível/read-only ou roll-forward; testar apenas compatibilidade com consumidor real identificado.

Ausência de mapa em engagement antigo deve aparecer como capacidade não avaliada, sem migração automática. Para continuar produção nessa versão, aplicar a política de compatibilidade já autorizada; para declarar a nova cobertura, criar e validar o mapa.

Antes de alterar uma execução/piloto em curso, fixar o SHA efetivamente usado e mudar apenas num ponto seguro. Uma atualização de main não significa que a sessão carregou as novas instruções. Registar versão adotada e segmento a partir do qual vale.


---

## Adenda v3.1 (25-09-2026)

### Decisões do mantenedor

1. **§2.11, edição de `library/` em desenvolvimento.** O procedimento autorizado é o override administrativo:
   - `AISA_GUARD_MODE=log` e remoção **local** da regra `deny Write/Edit(./library/**)`, só nas sessões de desenvolvimento das fases autorizadas;
   - repor antes de cada commit, com `git diff .claude/settings.json` vazio;
   - o commit leva só as alterações do kernel;
   - em execução de engagement, `library/` continua protegida.
2. **Revisor do mapa: vale o v3.** Não há agente novo. O MAP-19 fica com a revisão de fontes (`source_review`) e com o dono. Reavaliar depois do M5.
3. **Piloto do M5: Pricing Marinha.**
   - Pré-condição: os ficheiros reais autorizados (`PREÇO BANCAS.xlsm` e textos) em `projects/<slug>/inputs/`.
   - O artefacto de referência (fluxograma AS-IS) serve de expectativa de avaliação, **separada do contexto do autor** (M5 tarefa 1).
   - Sem os ficheiros, o M5 bloqueia.

### Correcções de facto ao v3 (verificadas neste checkout)

| # | v3 diz | Neste checkout | Acção |
|---|---|---|---|
| 1 | Evidência M0 sobre `c97ee1c`; `docs/process-map/M0/` existe | HEAD `2474a41`; `c97ee1c` e `docs/process-map/` ausentes | M0 refeito aqui (v3 M0 *Entrada*) |
| 2 | Erro de base F8 (cartões sem `entrega_inicial`) | `test_f8_tools.py`: 28 OK. Subset stdlib: 1 erro em `test_f7_compat.py` (commit `56cb4e1` ausente, clone raso). A suite completa não corre: faltam `openpyxl` e `python-docx` | M0: `git fetch --unshallow` + `pip install -r requirements-dev.txt`, depois a baseline |
| 3 | §6 "não introduzir `BASE_CHANGED`" | `operation.run` já tem os dois códigos: `BASE_CHANGED` (`expected`, ficheiro publicado) e `STALE_INPUT` (`read_set`, fonte consumida) | O mapa usa os dois como estão |
| 4 | §7 "ajustar a ordem se o índice só for reconstruído depois" | Confirmado: o índice é reconstruído no passo 6, mas a L2 lê-o no passo 5a2 | Corrigir a ordem no M1 (tarefa 1, junto com o P-0) |
| 5 | §5.3 `was` | O nome já existe (transição na SU; relação `was` no grafo) | Documentar: no mapa, `was` = lista de predecessores |
| 6 | §10 delimitador por confirmar | `\|` parte a tabela | `elementos`: ids separados por `, `; testar o `dashboard.parse_su` |
| 7 | — | O documento salta do §14 para o §16 | Renumerar ao commitar |

### Confirmações do v3 já verificadas

- Colisão `MAP-D-001` → `D-001`: confirmada (`resolve.cited_sources`). `MAPD-001` não colide.
- O inventário de cobertura só enumera PM e PM-U, não `CALC` nem etiquetas de §4 (`coverage.py:886-896`).
- `CITED_DIRS_RE` não inclui `_map/` (`resolve.py:1218`).
- `workflow.py` tem `validate` e `SUPPORTED`.
- `release.py` e `trace.py` não consultam a cobertura.
- `on-su-change.py` só reage a Write/Edit.
- Não existe a skill `aisa-resume`; o comando é `.claude/commands/resume.md`.
- Fixture F06: a v01 passa limpa na verificação estrutural, com C-007 e C-010 `missing`, e não é elegível para aprovação.
- `_capture/` não é protegido pelas guardas.
- A captura nunca lê o `enquadramento.md`.

### M0 — ajustes à execução

Tarefas do v3 M0, com os ajustes seguintes:
1. Branch `claude/claim-credit-endpoint-e2oqht` (designada nesta sessão). Registar o SHA e as alterações locais.
2. Commitar o plano v3 + esta adenda em `docs/process-map/PLANO.md` (persistência entre sessões; o upload não persiste).
3. Clone completo + dependências de desenvolvimento → baseline completa e subset stdlib, com as contagens reais.
4. Reproduzir num script (`docs/process-map/M0/reproduce.py`):
   - PM/CALC/§4 no inventário;
   - a colisão de ids;
   - F06;
   - a ordem índice/L2.
5. Matriz de leitores e escritores deste checkout, sem herdar números de linha.
6. Fixtures de aceitação (v3 M0 tarefa 7).
7. `docs/process-map/M0/RELATORIO.md` no formato do protocolo, com actualização do `consumer-matrix.json`.
8. Nenhuma edição a `library/` no M0: não é necessária.

### Verificação (por fase)

- Testes dirigidos + suite completa + subset stdlib, com as contagens reais, os skips e o not-run registados.
- Demonstração da fase (ver v3), com evidência.
- `git diff .claude/settings.json` vazio antes de cada commit.
- Parar para aprovação.
