# 07 — Migração, compatibilidade e rollout

## Política

Engagement existente não muda de perfil porque o código foi atualizado. Sem perfil persistido, identificar como legado: executar classic apenas se suportado; caso contrário, recusar escrita com orientação de leitura/migração. Ativação handoff exige seleção explícita e capacidade do pack. Uma opção global pode definir o default para novos engagements, nunca reescrever os anteriores.

O plano não obriga a migrar todos os engagements. Suporte classic na nova versão depende de consumidores reais identificados em F0, com âmbito e condição de retirada. Sem essa necessidade, conservar a versão histórica e acesso aos dados é suficiente; não manter runtime duplo. Corrigir bugs gerais de integridade pode beneficiar ambos, mas não alterar silenciosamente a semântica de admissão/gates classic.

## Matriz de compatibilidade a concretizar em F1

| Código | Engagement | Política |
| --- | --- | --- |
| Novo | Classic legado | Leitura/escrita apenas se contratada em F0; caso contrário rejeição segura, sem alterar dados |
| Novo | Handoff schema suportado | Leitura/escrita pelo perfil explicitado |
| Novo | Schema futuro desconhecido | Rejeição clara ou modo read-only explicitamente implementado |
| Antigo | Handoff novo | Não autorizado a escrever; bloqueio pela guarda de versão |
| Novo | Pack sem handoff | Classic suportado ou erro; nunca capacidade inventada |

Não basta o CLI conhecer a versão: hooks, tools e caminhos de escrita direta precisam de aplicar a mesma política. Testar os leitores antigos reais suportados; não assumir que respeitam um campo que nunca conheceram. Quando não respeitarem, isolar a versão antiga do engagement novo em vez de confiar numa guarda inexistente.

## Procedimento de migração

1. Confirmar engagement, revisão, autorizações e alvo. Verificar ausência de operação pendente, ou recuperar primeiro.
2. Executar dry-run que lista ficheiros/campos/referências alterados, gaps de desenho, incompatibilidades e reversibilidade.
3. Obter autorização de migração. Criar cópia de segurança recuperável com hashes e testar a sua leitura, sem incluir segredos novos.
4. Fixar o schema/perfil de destino e operation ID; aplicar transformação pelo coordenador.
5. Preservar fontes, IDs, estados epistémicos, decisões e aprovações nas respetivas revisões originais.
6. Mapear conteúdo funcional explícito já existente para FC com referências; texto ambíguo vira draft para revisão, nunca regra autorizada fabricada.
7. Marcar coverage/reviews/readiness do novo perfil como por verificar quando não houver evidência equivalente.
8. Gerar relatório before/after, campos não mapeados, limitações e próximo trabalho seguro.
9. Fazer cold resume e regenerar projeções. Só depois autorizar utilização do perfil novo.

Idempotência: repetir a mesma migração não duplica IDs nem reescreve autorizações. Uma interrupção produz recuperação, não um híbrido aceite. Não migrar schema enquanto outra sessão escreve com base antiga.

## O que não inferir dos dados antigos

- Seis ficheiros de lentes não provam coverage material do handoff.
- Blueprint aprovado não prova regra funcional detalhada nem trabalho completo.
- Documento final antigo não significa aceitação humana de nova revisão.
- Candidato revisto em paralelo não significa revisão do conjunto final publicado.
- Estimativa preliminar modo B não é estimativa modo A do inventário atual.
- Estado Confirmed não pode ser atribuído porque dois agentes disseram o mesmo.

Se a migração detetar confirmação possivelmente indevida, registar anomalia e pedir reavaliação pelo fluxo normal. Não mudar em massa estados existentes sem preservar histórico e autoridade.

## Rollback sem perda de conhecimento

Separar rollback de código e de dados. Voltar código não pode apagar FC/decisões/trabalho publicados depois da migração. Quando a versão anterior não lê o schema novo, usar versão compatível read-only/export ou corrigir por roll-forward.

Restaurar backup só como recuperação explicitamente autorizada, com comparação e preservação das alterações posteriores. Não automatizar restore sobre engagement ativo. Releases de handoff antigas conservam-se imutáveis e podem ficar marcadas obsoletas; não reescrever o pacote entregue para esconder a mudança.

## Rollout

1. Desenvolvimento e fixtures isoladas.
2. Opt-in interno com pacote experimental rotulado.
3. Pilotos supervisionados e destinatário independente.
4. Engagements reais voluntários, com monitorização de integridade/lacunas/custo.
5. Decisão explícita sobre default e descontinuação gradual do que ficou redundante.

Durante rollout, acompanhar falhas de publicação, stale outputs, bloqueios de retoma, perguntas essenciais do destinatário, divergências entre spec/backlog/estimate e regressões de coverage. Métricas medem trabalho, não guardam dados pessoais por conveniência.

## Stop conditions

Parar publicação/migração se houver perda de dados, conflito não resolvido, schema não suportado, autorização ausente, segredo exposto, falsa confirmação ou handoff falsamente declarado pronto. Preservar estado, produzir diagnóstico e próximo passo. Não contornar as guardas para fazer o piloto passar.
