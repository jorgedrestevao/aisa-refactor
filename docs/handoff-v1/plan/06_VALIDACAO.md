# 06 — Validação e pilotos

Esta é a especificação dos testes a implementar/executar, não um relatório de testes já passados. A validação automática comprova estrutura e comportamento programado; não prova por si que uma solução está correta, licenciada ou aceite pelo cliente.

## Inventário de testes

| ID | Cenário | Resultado esperado |
| --- | --- | --- |
| T01 | Reexecutar suite da baseline | Comandos/ambiente/resultados reproduzíveis; falhas prévias identificadas |
| T02 | Consumidor/writer não inventariado | Inventário e contract tests detetam caminho por adaptar |
| T03 | Engagement sem perfil | Resolve classic de forma documentada, sem migração implícita |
| T04 | Pack sem capacidade handoff | `UNSUPPORTED_PROFILE`; sem fallback silencioso |
| T05 | Regra de arredondamento não altera tecnologia | Admitida como material funcional, com teste de limite |
| T06 | Facto necessário sem valor conhecido | `fact_gap` válido sem alternativas artificiais |
| T07 | Pergunta sem impacto e N/A sem motivo | Estacionamento justificado; N/A inválido não fecha coverage |
| T08 | Agentes concordam sem evidência | Estado epistémico não é promovido |
| T09 | Cold resume sem conversa anterior | Reconstrói objetivo, autorizações, blockers e próximo trabalho correto |
| T10 | Read-set omite input efetivamente usado | `INCOMPLETE_READ_SET`; resultado não publicável |
| T11 | Input muda durante execução | `STALE_INPUT`; draft preservado e integração rejeitada |
| T12 | Crash em cada limite de publicação | Revisão antiga/nova consistente ou `RECOVERY_REQUIRED`, nunca mistura válida |
| T13 | Repetir operação após sucesso sem resposta | Mesmo efeito/receipt, sem duplicar itens |
| T14 | Duas sessões publicam da mesma base | Conflito explícito; nenhuma atualização perdida |
| T15 | Resultado recebido mas não integrado | Não conta para readiness; aparece na retoma |
| T16 | Contexto necessário excede orçamento | Estado parcial explícito e expansão/divisão; sem omitir blocker crítico |
| T17 | Edit direto SU, grafo divergente | Preservar edição, bloquear publicação inconsistente, reconciliar explicitamente |
| T18 | Uma análise cobre seis lentes | Fecha coverage válida sem seis ficheiros/execuções obrigatórios |
| T19 | Texto lista lentes sem tratar risco | Revisão semântica identifica gap; títulos não contam como prova |
| T20 | FC sem regra essencial ou aceitação | `BLOCKING_GAP` no âmbito afetado |
| T21 | Blueprint e FC contradizem mesma regra | Conflito visível; não escolhe uma versão silenciosamente |
| T22 | TO-BE aprovado com premissa AS-IS assumida | Autorização não confirma a premissa |
| T23 | Render encontra detalhe funcional em falta | Não inventa; devolve lacuna ao autor |
| T24 | Blueprint/FC mudam após aprovação | Aprovação da revisão antiga não autoriza a nova automaticamente |
| T25 | Options dispara revisão antes de candidatos | Execução recusada ou aguardando revisão publicada |
| T26 | Parecer refere candidato anterior | Marcado stale; não fecha finding atual |
| T27 | PP imposto | Analisa viabilidade/padrões sem shortlist artificial de plataformas |
| T28 | Risco concreto pede especialista | Mandato contém pergunta/input/output; seleção é explicável |
| T29 | Revisor necessita research/craft relevante | Acesso permitido e origem/versionamento registados |
| T30 | Limite de dialética atingido | Escala/permanece aberto; não aceita por esgotamento |
| T31 | Obrigação arquitetural de prova | Mapeada ao trabalho e condição de aceitação conforme contrato existente |
| T32 | Backlog/estimate discordam do inventário | Referências/revisões inconsistentes detetadas; sem esforço concorrente |
| T33 | Um subset tem blocker de build | Entrega total bloqueada; parcial só com exclusão autorizada e dependências coerentes |
| T34 | Prova futura pode invalidar viabilidade | Bloqueia compromisso aplicável; não escondida em checklist de implementação |
| T35 | Migração engagement antigo | Dados/estados/decisões preservados; novos campos sem evidência ficam por completar |
| T36 | Leitor antigo encontra schema novo | Falha clara/read-only suportado; sem truncar campos |
| T37 | Solução headless | Nenhuma UI/documento de ecrãs obrigatório sem aplicabilidade |
| T38 | Migração de legado | Reconciliação, cutover, rollback e retenção ligados a trabalho/aceitação |
| T39 | Pacote tem ficheiro alterado após release | Hash mismatch; release não aceite como intacta |
| T40 | Segredo em draft/output | Bloqueado/removido segundo política; referência segura preservada |
| T41 | Premissa altera regra/dados/arquitetura | Marca dependências reais stale e preserva itens não afetados |
| T42 | Mudança só editorial ou unidade não consumida do pack | Sem reabertura semântica indevida; byte revision continua exata |
| T43 | Destinatário em contexto novo recebe só pacote | Identifica trabalho e testes sem depender da conversa; lacunas registadas |
| T44 | Comparação classic vs novo | Qualidade material não inferior; custos/chamadas medidos sem alegações antecipadas |
| T45 | Slice numa sandbox real autorizada | Resultados observados e divergências registados; ausência de execução declarada |
| T46 | Aceitação humana | Registo explícito de versão/âmbito/condições/autoridade; simulação distinguida |

T19/T43/T44/T46 exigem julgamento humano ou avaliação assistida documentada; não reduzir a asserts de texto. T45 é teste de integração real condicionado a recursos/autorização. Os restantes devem ter fixtures automatizadas onde tecnicamente possível, complementadas por inspeção das instruções.

## Fixtures obrigatórias

1. **Escolha de solução:** processo com alternativas reais e decisão económica; inclui uma premissa não confirmada e um conflito entre fontes.
2. **PP constrained:** aprovação com dados e regras de cálculo, exceção, duplicação de pedido e permissões por papel. Contém regra material que não muda tecnologia.
3. **Change-impact:** alterar uma premissa após handoff aprovado e verificar invalidação seletiva, trabalho/estimate atualizados e preservação da decisão anterior.
4. **Headless:** automação/integração sem interface própria; testa N/A justificado e recuperação/idempotência.
5. **Substituição/migração:** dados históricos, qualidade, reconciliação, cutover, rollback e coexistência temporária.

Reutilizar fixtures existentes quando cobrem estes cenários. Cada fixture tem expected outcomes de conhecimento/decisão/rastreabilidade, não apenas output textual exato. Dados sintéticos são identificados como tal.

## Protocolo de piloto

Preparar para cada caso o mesmo source pack, scope e constraints para classic/novo. Registar versão de código, pack, modelo/configuração quando disponível e permissões. Não fornecer ao revisor independente a resposta esperada nem o histórico do autor.

Para obter uma comparação inicial, executar os três percursos principais pelo menos duas vezes por perfil: seis execuções de cada perfil. Incluir headless e migração entre os casos ou como extensões. Esta amostra é um gate exploratório, não uma demonstração estatística universal.

Em cada execução:

1. Capturar requisitos e desenhar solução, com inputs iguais e alterações registadas.
2. Interromper pelo menos uma vez antes de completar a tarefa e retomar sem histórico.
3. Injetar uma alteração material; medir deteção e retrabalho.
4. Congelar release; destinatário revê apenas pacote.
5. Registar perguntas essenciais não respondidas, contradições, exclusões e escolhas legitimamente delegadas.
6. Se autorizado, implementar slice representativo e comparar comportamento com contrato. Documentar configuração e resultados, sem expor segredos.

## Gates de qualidade

Proposta de critérios a confirmar em F0, antes de observar os resultados:

- 100% dos requisitos materiais do âmbito entregue com ligação a desenho, trabalho e aceitação, ou justificação explícita aplicável.
- Zero blockers globais/de build ocultos, contradições materiais abertas, confirmações sem evidência e aprovações inventadas.
- 100% dos cenários de conflito/crash/idempotência passam nos testes determinísticos.
- 100% das retomas do piloto preservam autorizações e questões materiais sem depender da conversa.
- Zero pergunta essencial do destinatário sem resposta/encaminhamento após uma ronda de correção do pacote final. Escolhas delegadas válidas não contam como falhas.
- Novo perfil não perde cobertura material face à avaliação adjudicada dos mesmos casos classic.
- Redução de chamadas/contexto é objetivo secundário medido. Meta inicial: menos execuções obrigatórias por round; não existe promessa de percentagem de poupança.

Se qualidade passar mas custo piorar, manter experimental e otimizar seleção/contexto antes de mudar default. Se custo melhorar mas qualidade falhar, NO-GO.

## Evidência e limites do relatório

Cada resultado tem ID, caso, revisão, comando/procedimento, output observado, resultado esperado, pass/fail/not-run, avaliador e limitações. Um teste não executado mantém `not-run`, mesmo quando o prompt diz que funcionará.

Reutilizar a disciplina do protocolo P8 para sessões reais, mas manter este estudo de refatorização identificado separadamente. O estado NO-GO de pilotos anteriores não desaparece por renomear o perfil.

Gates de release exigem suite verde ou exceções explicitamente aceites que não afetem integridade/segurança/verdade de readiness. Não aceitar exceção para corrupção, perda de dados ou falsa confirmação. Aceitação do pacote não comprova desempenho/capacidade no tenant sem teste real correspondente.
