# 02 — Contratos-alvo

Regras desta página são normativas para `handoff-v1`. `classic` só mantém execução suportada na nova versão quando F0 demonstrar essa necessidade, conforme 09_DEPENDENCIAS_E_TESTES.md; dados não migrados não são reinterpretados automaticamente. Nomes físicos de ficheiros novos são propostas a fixar em F1; campos e semântica não devem ficar implícitos em prompts.

## 1. Fronteiras kernel / pack / engagement

| Camada | Responsabilidade | Não faz |
| --- | --- | --- |
| Kernel | Identidades, evidência, estados, tarefas, coordenação, revisão, dependências, readiness, retoma | Escolher produto PP ou codificar uma regra de negócio do cliente |
| Pack PP | Capacidades, conhecimento, padrões, riscos, contratos de desenho PP, templates e validações específicas | Promover factos do cliente ou contornar uma autorização |
| Engagement | Fontes, contexto, âmbito, decisões, desenho autorizado, trabalho, provas e entregas | Copiar conhecimento genérico como se fosse evidência observada |

Pack declara `supported_workflow_profiles`, `supported_routes`, `design_contract_version`, tipos de especialista e capacidades de handoff. Ausência de declaração significa não suportado; não inferir compatibilidade dos packs skeleton generic/Mendix/OutSystems. Fallback permitido só para um perfil que esses packs declarem suportar.

## 2. Autoridades e relações

| Conteúdo | Autoridade | Consumidores |
| --- | --- | --- |
| Evidência original | Fontes preservadas e índice existente | SU, análise, revisores |
| Alegação e estado epistémico | SU, com espelho no grafo conforme contrato atual | Decisão, desenho e readiness |
| Escolha autorizada, motivo, alternativas e triggers | Registo de decisões existente | Blueprint, contrato funcional, revisita |
| Topologia, responsabilidades, fronteiras e obrigações arquiteturais | Blueprint aprovado existente | Contrato funcional e implementation-spec |
| Semântica detalhada de comportamento TO-BE | Novo artefacto `_design/functional-contracts.json` | Blueprint por referência, spec, testes |
| Trabalho build/config, sequência, migração/cutover, aceitação | Implementation-spec existente | Backlog e estimativa |
| Esforço | Estimate existente | Planeamento e resumo executivo |
| Trabalho do próprio AISA em curso | Novo `_work/checkpoint.json` | Retoma, router e observabilidade |
| Índice de entrega | Projeção de uma revisão consistente | Destinatário e verificação de release |

SU não passa a armazenar toda a especificação funcional: guarda alegações/questões e ligações. Blueprint não duplica regras; referencia IDs funcionais. Implementation-spec não redefine comportamento: converte contratos autorizados em trabalho e aceitação. Backlog não se torna outra fonte de esforço ou de desenho.

A aprovação do TO-BE é uma decisão humana autorizada; não transforma automaticamente uma premissa AS-IS em Confirmed. Uma regra normativa pode ser escolhida sem ter sido observada no sistema anterior. Registar a distinção `observed_as_is` / `proposed_to_be` / `authorized_to_be` sem criar estados epistémicos adicionais.

## 3. Identificadores e versionamento

Reutilizar os IDs existentes para fontes, SU, decisões, arquitetura e provas. Novos IDs funcionais `FC-0001`, jornadas `J-0001` e trabalho `WP-0001` devem ser estáveis no engagement, não reutilizados após retirada. Confirmar em F0 se já existe namespace equivalente antes de introduzir outro.

Cada artefacto canónico novo tem `schema_version`, `engagement_id`, `revision`, `based_on` e `items`. `based_on` aponta para revisões/hashes de inputs, não só para nomes. Conteúdo publicado é imutável por revisão; o pointer de revisão corrente é controlado pela operação. Migração de schema não altera significado silenciosamente.

Distinções obrigatórias:

- Estado epistémico: os cinco estados atuais, sem um sexto para “aprovado”.
- Estado de tarefa: `planned`, `running`, `blocked`, `completed`, `cancelled`.
- Estado de resultado: `draft`, `received`, `integrated`, `superseded`.
- Autorização: referência ao ato e autoridade competentes, ou ausência dele.
- Freshness: `current`, `stale`, `unverified`; derivada das dependências.

`completed` exige output integrado ou encerramento justificado. Aprovação é propriedade de uma revisão e âmbito; nunca apenas de um filename.

## 4. Nova materialidade

Admitir uma questão quando a sua resposta possa alterar pelo menos um destes aspetos do âmbito:

1. Decisão de solução/arquitetura e os eixos técnicos existentes.
2. Correção funcional, cálculo, transição, exceção ou resultado de negócio.
3. Critério de aceitação, obrigação contratual ou evidência necessária.
4. Segurança, privacidade, operação, suporte, migração ou recuperação.
5. Viabilidade de implementação, dependência, custo ou esforço material.

Tipos: `fact_gap`, `design_choice`, `conflict`, `proof_obligation`. Um facto em falta não precisa de duas respostas fabricadas. Uma escolha de desenho explicita alternativas quando genuinamente disponíveis. Cada questão tem `impact`, `affected_scope`, `owner_role`, condição de fecho e referências; ausência de impacto demonstrável permite estacionar/retirar, com motivo.

Prioridade e bloqueio são diferentes. Uma questão de arredondamento pode não mudar tecnologia e ainda assim bloquear a aceitação de uma jornada financeira. Um detalhe de cor pode ser delegado, salvo requisito explícito de acessibilidade/identidade/contrato. Não deduzir materialidade pelo tamanho do texto.

## 5. Rotas

| Rota | Entrada | Saída de Options | Salvaguarda |
| --- | --- | --- | --- |
| `solution-choice` | Plataforma ainda aberta | Conjunto pequeno de candidatos realmente aplicáveis e trade-offs | Não reduzir a shortlist sem motivo |
| `platform-constrained` | Plataforma imposta e autoridade identificada | Variações de arquitetura/implementação e verificação de viabilidade | Não inventar três tecnologias; declarar incompatibilidade se existir |
| `change-impact` | Baseline aprovada + mudança | Delta, raio de impacto, decisões a reabrir, trabalho/provas afetados | Não repetir todo o discovery nem considerar intacto o que depende da mudança |

Rota é explícita, justificada e persistida. Mudança de rota cria revisão e reavalia dependências. “PP imposto” não significa Dataverse/Canvas/Power Pages obrigatórios nem ausência de análise de alternativas arquiteturais.

## 6. Lentes e coverage

As seis lentes mantêm os significados business, operations, user, data, governance e financial. Uma única análise pode cobrir várias. Coverage por dimensão tem `assessed`, `gap` ou `not_applicable`, referências e justificação. `assessed` significa examinada, não resolvida nem aprovada. `not_applicable` sem motivo é inválido.

Fechar um round no novo perfil depende de coverage material, não de seis ficheiros/assinaturas. Manter exceções e objeções; um texto que menciona todos os títulos não prova cobertura. Avaliação semântica requer revisão, para além de validação estrutural automatizada.

## 7. Contrato funcional

Cada `FC` inclui:

- Identidade, âmbito/jornada, propósito, responsável e revisão.
- Referências a requisitos/SU, decisões autorizadoras e elementos do blueprint.
- Atores e direitos necessários; precondições e trigger.
- Inputs com domínio, obrigatoriedade, validação e valores por omissão autorizados.
- Regra/algoritmo ou transição, pós-condições e invariantes.
- Resultados observáveis, mensagens relevantes e side effects.
- Exceções, duplicação/repetição, cancelamento, concorrência e recuperação quando aplicáveis.
- Exemplos de aceitação positivos, negativos e de limite; unidades e arredondamento quando existam cálculos.
- Dependências, escolhas delegadas, questões abertas e provas necessárias.

Campos não aplicáveis têm motivo; não inventar números para preencher. A definição lógica de uma entidade/campo continua no dono de dados do blueprint. O FC referencia esse campo e especifica como o comportamento o usa. Um parâmetro ainda por escolher exige envelope, responsável e teste de aceitação ou permanece blocker.

O autor funcional propõe o FC. O arquiteto verifica realizabilidade e correspondência ao blueprint. O responsável de negócio autoriza semântica material. Alteração posterior reabre só as aprovações/outputs dependentes, conforme o raio de impacto.

## 8. Readiness e bloqueios

As quatro fases existentes mantêm-se. Dentro de Decision, acompanhar `decision_ready`, `design_ready` e `handoff_ready` como predicados derivados; não como novos estados da SU ou quinta fase.

| Predicado | Condição mínima |
| --- | --- |
| `decision_ready` | Critérios/candidatos comparáveis, premissas e riscos materiais explícitos, blockers da escolha resolvidos ou risco autorizado admissível |
| `design_ready` | Âmbito e arquitetura autorizados; regras e interfaces essenciais especificadas; nenhuma contradição bloqueante de desenho |
| `handoff_ready` | Design pronto + inventário completo rastreável, aceitação, dependências, operação/ALM/migração aplicáveis, estimativa modo A, outputs atuais e consistentes, zero blockers de build no âmbito entregue |

Além deles, apresentar separadamente `integrity_ok`, `required_approvals_present`, `receiver_review_complete` e `receiver_accepted`. Nunca colapsar tudo num verde sem explicar o que foi verificado.

Questões abertas classificam-se em:

- `blocks_all`: impede compromisso/implementação global.
- `blocks_scope`: impede componentes/jornadas explícitos; podem ser excluídos da entrega parcial autorizada.
- `delegated_choice`: equipa pode decidir dentro de envelope e critério de aceitação definidos.
- `implementation_proof`: prova planeada com trabalho, dono, pré-requisitos e critério; se o resultado puder invalidar a viabilidade, é blocker anterior ao compromisso, não mera prova futura.

Aceitação de risco não substitui requisito legal, controlo obrigatório ou autorização de terceiro. Se um subset sair do âmbito, retirar também suas promessas, dependências incompatíveis e esforço não incluído; declarar exclusões na capa.

## 9. Interfaces mínimas a implementar

O módulo de workflow expõe funções puras para `validate_profile`, `plan_review`, `evaluate_readiness`, `build_resume_plan` e adaptadores de publicação pelo coordenador existente. As assinaturas concretas são congeladas em F1 com schemas de request/response e testes; não adicionar um CLI alternativo para cada função.

Respostas estruturadas incluem `ok`, `code`, `reasons[]`, `affected_ids[]`, `input_revision` e `next_actions[]`. Códigos estáveis mínimos: `UNSUPPORTED_PROFILE`, `STALE_INPUT`, `INCOMPLETE_READ_SET`, `AUTHORIZATION_REQUIRED`, `INTEGRITY_FAILURE`, `SCHEMA_UNSUPPORTED`, `BLOCKING_GAP`, `RECOVERY_REQUIRED`.

Integridade falhada bloqueia publicação; gate de fase pode aconselhar sem bloquear exploração. Um pedido de handoff final, porém, não passa com blockers escondidos: produz estado incompleto e lista do que falta, nunca uma falsa certificação.
