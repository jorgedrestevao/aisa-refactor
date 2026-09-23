# 05 — Plano de implementação faseado

Cada fase produz código/contratos, testes e um relatório conforme `templates/RELATORIO_FASE.md`. Fases são incrementos deste programa de refatorização, não novas fases do workflow de engagement. Não declarar duração ou orçamento de engenharia sem medir F0/F1.

Dependência principal: F0 → F1 → F2 → F3 → F4 → F5 → F6 → F7 → F8 → F9. Trabalho documental/test fixtures pode ser preparado antes, mas nenhum gate é saltado. Ao terminar F5 já deve existir um percurso vertical experimental; F6/F7 expandem e completam, não adiam toda a validação até ao fim.

## F0 — Fixar baseline e preparar segurança da mudança

**Objetivo:** saber exatamente o que se preserva e qual o custo atual.

Trabalho:

1. Inspecionar `AGENTS.md`, estado git e SHA da branch escolhida sem sobrescrever trabalho do utilizador. Comparar com o SHA deste plano e registar delta.
2. Inventariar escritores/leitores de SU, decisões, blueprint, coverage, spec, estimate e `_state.json`; resolver caminhos reais dos templates e skills/comandos.
3. Executar a suite documentada no repositório e registar comando, ambiente, exit code, falhas existentes e tempo. Não converter falha antiga em “passa”.
4. Criar fixtures mínimas dos três percursos e casos funcionais/headless/migração, sem dados de cliente.
5. Inventariar o protocolo P8 e evidência disponível. Resultados antigos com bloqueios conhecidos não contam como validação do perfil novo.
6. Definir métricas base: chamadas de agentes, unidades/tokens de contexto quando observáveis, retrabalho, questões materiais preservadas, inconsistências e perguntas do destinatário.

**Componentes:** testes/docs e inventário; sem mudança de comportamento de produção.

**Entregáveis:** matriz de consumidores, baseline de testes, fixture registry, delta ao plano, lista de decisões técnicas a fechar em F1.

**Gate:** baseline reproduzível e falhas conhecidas classificadas; todos os ficheiros-alvo resolvidos. Testes T01/T02.

**Rollback:** nenhum runtime alterado; remover só fixtures próprias se necessário, sem apagar outputs do utilizador.

## F1 — Congelar contratos e perfil opt-in

**Objetivo:** eliminar ambiguidades antes de alterar agentes e persistência.

Trabalho:

1. Formalizar `classic`/`handoff-v1`, seleção explícita por engagement, versão de schema e capability check do pack.
2. Rever materialidade/P26/Unknown em todos os contratos e consumidores do perfil novo. Manter cinco estados; introduzir tipo de questão e impacto sem promoção de dados antigos.
3. Definir schemas formais para perfil, tarefa/checkpoint, contrato funcional e índice de handoff. Campos adicionais desconhecidos não podem ser descartados silenciosamente.
4. Fixar autoridade de cada campo e namespace, incluindo reuso dos IDs existentes.
5. Especificar readiness, erros estruturados, política de revisão e aprovação por âmbito/revisão.
6. Ajustar guardas de ordem das lentes e completude para dispatch por perfil. O caminho classic mantém os testes de contrato existentes.
7. Documentar as alterações incompatíveis e a tabela leitor/escritor/schema.

**Componentes:** kernel contracts, CLAUDE, pack.yaml, hooks profile-aware, schemas e funções puras iniciais de workflow.

**Entregáveis:** contratos implementáveis; perfil novo selecionável mas ainda não anunciado como handoff operacional.

**Gate:** T03–T08, T35/T36; requisitos funcionais materiais já não são descartados; pack incompatível falha claramente.

**Rollback:** desativar perfil experimental; nenhum engagement classic necessita de migração.

## F2 — Continuidade transacional mínima

**Objetivo:** tornar retoma e publicação seguras antes de aumentar a autonomia dos papéis.

Trabalho:

1. Implementar checkpoint por referências e estados de tarefa/resultado separados.
2. Estender bootstrap com read-set adicional explícito, hashes e revisão consumida.
3. Integrar checkpoint e mutações de autoridades no coordenador existente; receipts/idempotency e conflitos verificáveis.
4. Impedir consumo de drafts como verdade; tratar resultados stale e integrações repetidas.
5. Implementar diagnóstico/recuperação e cold resume com budget e estado parcial explícito.
6. Atualizar hooks para guardar integridade sem motor transacional duplicado; documentar edição direta e reconciliação.
7. Testar falha injetada nos limites de publicação e concorrência de duas sessões.

**Componentes:** operation/bootstrap/resolve/graph/migrate, adaptador workflow, hooks, comandos resume/status.

**Entregáveis:** retoma baseada no repositório e protocolo de recuperação testado; ainda sem mudar toda a análise.

**Gate:** T09–T17. Nenhum leitor considera conjunto misto como revisão válida; dupla integração é idempotente.

**Rollback:** manter revisões novas preservadas; desativar escrita experimental e usar leitor compatível/recovery. Não restaurar cópia antiga por cima de trabalho recente.

## F3 — Análise integrada e materialidade funcional

**Objetivo:** produzir conhecimento utilizável sem seis execuções obrigatórias.

Trabalho:

1. Adaptar analista integrado para aplicar seis lentes, publicar coverage e questões materiais.
2. Converter conteúdo útil das lentes em checklists reutilizáveis, mantendo agentes classic.
3. Implementar admissão de fact_gap/design_choice/conflict/proof_obligation e impacto por âmbito.
4. Preservar origem AS-IS vs proposta/decisão TO-BE; distinguir facto confirmado e regra autorizada.
5. Atualizar capture/round/frame/answer/status e respetivos validadores.
6. Demonstrar que redução de chamadas não elimina regras, exceções e questões financeiras/compliance.

**Entregáveis:** percurso Discovery/Framing do perfil novo, com coverage rastreável e handoff ainda explicitamente incompleto.

**Gate:** T05–T08, T18/T19; fixture com arredondamento e ausência de valor factual permanece visível e corretamente classificada.

**Rollback:** voltar ao executor classic para engagements compatíveis; manter conhecimento capturado sem rebaixar estados ou apagar campos novos.

## F4 — Autoria funcional e primeiro desenho coerente

**Objetivo:** preencher a semântica que o render está proibido de inventar.

Trabalho:

1. Implementar artefacto FC e fluxo draft → revisão → integração → autorização da revisão/âmbito.
2. Integrar o modo autor funcional no workflow/comando de desenho existente; se for necessário novo comando, usar um único `aisa-design`, não outro pipeline paralelo.
3. Mapear comportamento, entidades/campos do blueprint, atores, direitos, exceções e exemplos de aceitação por ID.
4. Validar que blueprint e FC não possuem duas versões contraditórias da mesma regra; bloquear publicação afetada até reconciliação.
5. Fazer um percurso pequeno com jornada, dados, automação, recuperação e teste; sem obrigação de UI quando headless.
6. Ligar permissões de aprovação a papéis reais e não assumir que um agente pode aprovar pelo cliente.

**Componentes:** blueprint contract, FC schema, workflow, skill/comando de desenho, templates e validadores.

**Entregáveis:** desenho funcional e arquitetural de fixture única, com autorizações sintéticas claramente identificadas como dados de teste.

**Gate:** T20–T24; renderer rejeita preencher uma regra em falta; referência e aprovação stale bloqueiam publicação final.

**Rollback:** FC permanece em revisão preservada; retirar capacidade de emissão de handoff desse perfil até recuperação.

## F5 — Candidatos comuns, especialistas e primeiro percurso vertical

**Objetivo:** provar o ciclo completo em escala pequena antes da expansão.

Trabalho:

1. Implementar três rotas e router explicável por competência/risco.
2. Publicar candidatos antes de disparar revisores; fixar revisão e input set de todos os pareceres.
3. Aplicar mandatos/output contracts dos especialistas e acesso seletivo ao pack para autor e revisor.
4. Corrigir chairman: concordância não promove evidência; findings têm disposição e condição de fecho.
5. Aplicar revisão dialética limitada e escalamento.
6. Percorrer uma fixture PP constrained desde captura até desenho, implementation-spec e estimate usando templates existentes; gerar handoff experimental e submetê-lo a uma sessão nova.
7. Registar lacunas do destinatário, chamadas, contexto e retrabalho. Corrigir lacunas sistémicas antes de aumentar cobertura.

**Componentes:** orchestration, options/decide/revisit, agentes/mandatos, pack knowledge metadata, artefactos de revisão existentes.

**Gate:** T25–T30 e primeiro ensaio T43. Todas as revisões referem a versão correta; zero confirmação por maioria; handoff incompleto é rotulado como tal.

**Rollback:** perfil novo permanece experimental; classic intacto. Desativar router novo sem eliminar pareceres e decisões.

## F6 — Rastreabilidade completa e handoff implementável

**Objetivo:** transformar o percurso vertical num pacote completo para o âmbito contratado.

Trabalho:

1. Estender templates existentes conforme matriz de `08_HANDOFF.md`; não criar onze documentos obrigatórios.
2. Ligar requisito/regra → FC → elemento arquitetural → WP → teste/prova; encontrar órfãos e justificações de não aplicável.
3. Preservar implementation-spec como dono do inventário e estimate como único dono do esforço; backlog deriva do inventário.
4. Completar ALM, security enforcement, integração/recovery, migração/cutover, operação e dependências de cliente quando aplicáveis.
5. Gerar índice de handoff com hashes, revisões lidas, scope incluído/excluído, aprovação e limitações.
6. Implementar gates por âmbito e aceitação do destinatário independente de readiness técnica.
7. Assegurar que todas as obrigações de prova têm trabalho e aceitação, sem afirmar execução não ocorrida.

**Gate:** T31–T34, T37–T40. Zero requisito material órfão no âmbito entregue; esforço por WP coerente; pacote parcial não é apresentado como completo.

**Rollback:** suspender publicação final; conservar drafts/revisões anteriores e explicar obsolescência.

## F7 — Mudanças, migração e compatibilidade

**Objetivo:** suportar evolução real sem refazer tudo nem perder conhecimento.

Trabalho:

1. Implementar raio de impacto e stale transitivo reutilizando grafo/fingerprints.
2. Implementar migração dry-run, cópia de segurança validada, versão suportada e relatório de campos não mapeados.
3. Exercitar engagement classic antigo, novo handoff, migração interrompida e retoma com versão anterior do código.
4. Não promover factos, inventar aprovações ou transformar pareceres antigos em revisão independente.
5. Atualizar docs de setup, manutenção, recuperação e responsabilidades de acesso/backup.

**Gate:** T35/T36/T41/T42; rollback preserva novas informações e bloqueia downgrade destrutivo.

**Rollback:** rollback de código só com leitor compatível; caso contrário modo read-only/export e roll-forward corretivo.

## F8 — Pilotos adversariais e aceitação do destinatário

**Objetivo:** demonstrar utilidade, continuidade e custo, para além de schemas válidos.

Trabalho:

1. Executar protocolo de `06_VALIDACAO.md` nos três percursos, incluindo migração e headless.
2. Comparar classic/novo perfil sobre casos equivalentes, mantendo fontes e objetivos; medir qualidade antes de eficiência.
3. Fazer cold resume sem histórico e mudança de premissa a meio do processo.
4. Revisor destinatário recebe só pacote; se equipa real disponível, pedir aceitação explícita de versão/âmbito.
5. Realizar slice de implementação numa sandbox autorizada, apenas se houver autorização/recursos; ausência é reportada, não simulada como prova real.
6. Corrigir causas sistémicas e repetir os cenários afetados, guardando resultados falhados.

**Gate:** T43–T46 e critérios quantitativos da validação. Simulação sozinha permite continuar experimental, não reivindicar aceitação humana ou eficácia de produção.

**Rollback:** manter classic default e publicar relatório de NO-GO com blockers; não forçar adoção para cumprir calendário.

## F9 — Rollout controlado e simplificação final

**Objetivo:** adotar só o que foi demonstrado e remover duplicação de forma segura.

Trabalho:

1. Selecionar engagements voluntários e registar perfil explicitamente.
2. Disponibilizar runbook de suporte, métricas, incidentes e rollback.
3. Rever resultados após um conjunto acordado de casos concluídos, não apenas número de dias.
4. Mudar default só com decisão explícita do mantenedor e gates cumpridos. Não converter engagements existentes automaticamente.
5. Deprecar prompts/branches de workflow redundantes com janela de compatibilidade documentada; manter leitor/export de versões suportadas.
6. Consolidar documentação; arquivar planos superados com link para fonte normativa atual.

**Gate:** regressão completa, compatibilidade comprovada, destinatário/pilotos documentados e autorização de release. Sem estes elementos: manter opt-in.

**Rollback:** voltar default a classic para novos engagements; existentes handoff continuam em versão compatível/read-only até correção.

## Definition of Done comum

- Contrato, implementação, hooks, exemplos e documentação concordam.
- Testes da fase e regressões relevantes executados; comandos/resultados anexados.
- Nenhuma alteração fora do âmbito, dado de cliente exposto ou aprovação inventada.
- Estado persistido permite a outro executor retomar sem esta conversa.
- Falhas/limitações são explícitas; “não executado” não se converte em “passou”.
- Próxima fase e pré-requisitos identificados; merge/push apenas quando autorizados.
