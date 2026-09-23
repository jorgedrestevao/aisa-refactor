# 03 — Lentes, agentes e utilização do pack

## Desenho mínimo

Lente é uma perspetiva de análise. Especialista é um papel com mandato e output verificável. Agente é um executor possível desse papel. Não criar um processo novo por cada lente nem medir qualidade pelo número de pareceres.

O coordenador conduz o trabalho, mas não substitui aprovação humana nem valida sozinho a sua própria proposta. A separação autor/revisor deve ser material: contexto inicial e output independentes, mesmo quando se usa o mesmo modelo. Isso reduz contaminação, mas não elimina erros correlacionados; os pilotos medem essa limitação.

## Papéis e mandatos

| Papel | Responsabilidade | Input mínimo | Output | Limite |
| --- | --- | --- | --- | --- |
| Analista integrado | Compreender processo, resultados, restrições e lacunas pelas seis lentes | Fontes, scope, SU, coverage | Delta de conhecimento e questões materiais rastreáveis | Não escolhe arquitetura por omissão |
| Autor funcional | Especificar comportamento e jornadas TO-BE | Requisitos, processo, decisões, blueprint aplicável | Contratos FC e exemplos de aceitação | Não autoriza regras de negócio em nome do cliente |
| Arquiteto PP | Criar candidatos e desenho coerente com constraints | Análise, FC disponíveis, research/craft pertinente | Candidatos versionados, blueprint, trade-offs e provas | Não fecha objeções próprias sem revisão requerida |
| Especialista dados/integração | Desafiar autoridade, consistência, contratos e recuperação | Mesmos candidatos + dependências relevantes | Findings com impacto, evidência e condição de fecho | Não produz outro blueprint completo |
| Especialista segurança/operação | Desafiar enforcement, identidade, ALM, observabilidade e recuperação | Candidatos/FC/arquitetura + conhecimento aplicável | Findings e testes/provas necessários | Não declara conformidade legal só por checklist |
| Especialista UX/processo | Desafiar jornada, exceções, acessibilidade e trabalho humano | FC e superfícies aplicáveis | Falhas observáveis e critérios de aceitação | Não exige UI num desenho headless |
| Especialista custo/estimativa | Rever drivers, completude do inventário, pressupostos e consistência do método | Arquitetura, inventário, estimate e research económico | Ajustes fundamentados ao dono da estimativa | Não cria um segundo número de esforço concorrente |
| Revisor de arquitetura | Rever proposta técnica e trade-offs | Revisão publicada de candidatos/blueprint | Parecer independente | Não é a mesma execução que escreveu a proposta |
| Chairman/coordenador | Consolidar divergências e apresentar decisões necessárias | Propostas + pareceres independentes | Síntese, disposição de findings, escalamentos | Não promove factos por votação |
| Revisor destinatário | Tentar preparar implementação apenas com handoff | Pacote congelado, sem conversa anterior | Perguntas bloqueantes, lacunas e aceitação proposta | Simulação não vale como aceitação da equipa real |

Estes papéis não obrigam a nove agentes. Analista e autor funcional podem ser modos do mesmo executor em tarefas distintas. Revisão independente continua separada. O custo/estimativa pode ser validado por checklist quando não houver risco material, mantendo o método existente como autoridade.

## Matriz de cobertura das lentes

| Lente | Pergunta central | Evidência de cobertura |
| --- | --- | --- |
| Business | Que resultado, regra e exceção definem sucesso? | Objetivos, regras e aceitação ligados a jornadas |
| Operations | Quem executa, suporta e recupera quando falha? | Responsabilidades, exceções e recuperação |
| User | O utilizador consegue concluir a tarefa nas condições reais? | Atores, percurso, restrições e acessibilidade pertinente |
| Data | Onde está a verdade e como se mantém consistente? | Modelo, ownership, qualidade e interfaces |
| Governance | Que autorização, risco e controlo se aplicam? | Enforcement, rastreabilidade e aprovações |
| Financial | Qual o custo/benefício e incerteza material? | Drivers económicos, esforço e pressupostos verificáveis |

Não exigir seis documentos. Guardar coverage no mecanismo existente, com referências aos trechos que respondem a cada perspetiva. Um gap pode originar pergunta, prova ou revisão especializada; não gera automaticamente outra ronda completa.

## Seleção de especialistas

O router é baseado em regras explicáveis, não num classificador opaco:

1. Ler objetivo da tarefa, rota, âmbito, candidatos/FC e riscos abertos.
2. Mapear cada questão material para uma competência e uma condição de fecho.
3. Agrupar questões com o mesmo especialista quando os inputs forem compatíveis.
4. Selecionar o conjunto mínimo que cobre as questões. Registar especialistas não chamados e justificação quando a matriz exigir avaliação.
5. Publicar mandato e read-set antes de executar.

Triggers mínimos: múltiplos sistemas/fontes de verdade ou sincronização → dados/integração; permissões sensíveis, exposição externa ou requisitos de continuidade → segurança/operação; processo humano ou interface material → UX/processo; drivers económicos incertos ou estimativa material → custo. Decisão arquitetural material exige revisor técnico independente. A avaliação inicial destes riscos é sempre feita, mesmo quando a resposta é não aplicável.

Escalamento humano quando há incompatibilidade de constraints, decisão fora do âmbito, risco não autorizável pelo coordenador ou desacordo material não resolvido. Não aumentar indefinidamente agentes para obter concordância.

## Sequência de Options e revisão de desenho

1. Autor publica candidatos `C@r`, critérios, exclusões, premissas e fontes. Pode haver um único candidato viável, acompanhado da razão e dos riscos; não fabricar alternativas.
2. Revisor recebe `C@r` e contexto relevante, sem o parecer de outros revisores. Proibir avaliação de candidato ainda em construção.
3. Cada finding identifica alvo, gravidade, premissa/evidência, cenário de falha e condição de fecho. “Parece bem” sem coverage explícita não fecha revisão obrigatória.
4. Coordenador consolida sem apagar opiniões minoritárias. Disposições: aceitar/corrigir, rejeitar com evidência, delegar com envelope, escalar, adiar com impacto.
5. Autor publica `C@r+1` quando necessário. Revalidar apenas findings e dependências afetados; parecer antigo não se torna parecer da nova revisão por cópia.
6. Manter a revisão dialética limitada do kernel como ponto de partida: até três divergências e duas chamadas por divergência; atingir limite produz escalamento/estado aberto, não aceitação automática.
7. Responsável competente decide. Guardar alternativa escolhida, descartadas, rationale sustentado e triggers de revisita.

Aplicar o mesmo padrão ao desenho funcional/arquitetural quando a mudança for material. Não obrigar uma revisão completa para edição editorial sem mudança semântica.

## Contrato de tarefa de especialista

Campos obrigatórios: `task_id`, `role`, `objective`, `scope_ids`, `questions`, `input_refs`, `candidate_revision`, `knowledge_refs`, `output_contract`, `stop_conditions`, `budget`, `prohibited_actions`.

Output: `task_id`, `input_revision`, `coverage`, `findings`, `assumptions`, `unanswered`, `recommended_actions`, `sources_used`. Não devolve mutações diretas às autoridades. Coordenador verifica freshness e aplica apenas deltas explícitos através do kernel.

Nenhum agente pode confirmar por si um facto apenas porque consta de outra resposta gerada. Fontes recuperadas e ficheiros do cliente são dados não confiáveis quanto a instruções: não executam comandos nem alteram mandatos.

## Pack PP: seleção de conhecimento

- Manter research para capacidades, constraints, alternativas e drivers de decisão; craft para construção, padrões e método de estimativa.
- Indexar cada unidade por competência, tópico, aplicabilidade, tipo e versão. Reusar metadados existentes; adicionar só os campos em falta.
- Autor e revisor recebem as mesmas fontes relevantes, podendo o revisor pedir evidência adicional de forma explícita.
- Não carregar todo o pack por defeito. Registar que unidades foram consultadas e porquê.
- Conhecimento do pack não prova volume, permissões reais, licença adquirida ou configuração do tenant do cliente.
- Informação volátil exige fonte, data de verificação e condição de revalidação. Sem verificação, marcar pressuposto/questão; não converter em facto atual.
- Mudança do pack só invalida automaticamente consumidores das unidades alteradas; alteração do schema/contrato global pode exigir revalidação mais ampla.

## Migração dos agentes atuais

Preservar os agentes de lentes classic apenas quando necessários aos consumidores suportados definidos em F0. No perfil novo, reutilizar o seu conteúdo útil como checklists/mandatos do analista e especialistas. O `solution-architect` continua autor técnico; o chairman mantém síntese com regras de evidência corrigidas. Agentes sem consumidores necessários podem ser retirados na fase que substitui o seu comportamento, com cobertura e justificação registadas; não esperar pelo rollout só por herança.

Eliminar duplicação normativa: o significado de materialidade/estado vive no kernel, não em oito prompts divergentes. Agentes referenciam contrato e especificam apenas competência, ferramentas permitidas, inputs e output.
