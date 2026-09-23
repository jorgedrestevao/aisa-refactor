# 08 — Especificação do handoff end-to-end

## Princípio

O pacote contém o necessário para implementar o âmbito autorizado. Não tem de usar todos os produtos Power Platform nem conter um documento separado por domínio. Reusar discovery, blueprint, implementation-spec, estimate e vistas executivas existentes. Cada vista aponta para a mesma revisão de conhecimento/desenho.

Um índice de release declara engagement, scope, exclusões, versões de código/pack, revisões de inputs, ficheiros/hashes, autorizações, prontidão, provas realizadas/pendentes e aceitação do destinatário. Não incluir segredos ou dados de produção desnecessários.

## Matriz de conteúdo obrigatório por aplicabilidade

| Domínio | Informação necessária para implementar | Dono e verificação |
| --- | --- | --- |
| Âmbito/processo | Objetivos, atores, jornadas, fronteiras, AS-IS/TO-BE, incluído/excluído, dependências de cliente | Contexto/decisões; todas as jornadas entregues identificadas |
| Comportamento funcional | Regras, inputs/outputs, estados/transições, cálculos, exceções, cancelamento, exemplos positivos/negativos/limite | FC; sem decisões essenciais escondidas em prosa vaga |
| Dados | Entidades, identificadores/chaves, tipos lógicos, nulabilidade, defaults autorizados, relações, ownership, ciclo de vida, qualidade, retenção/eliminação e fonte de verdade | Blueprint/dados; FC referencia IDs, não redefine campos |
| Aplicações/experiência | Superfícies aplicáveis, navegação, ações por papel, validação, mensagens, estados vazios/erro, acessibilidade e limitações relevantes | Blueprint + FC; N/A válido para headless |
| Automação | Trigger, guardas, transições, efeitos, concorrência, reexecução, idempotência, falha/recovery e intervenção humana | Blueprint + FC; trabalho/testes cobrem caminhos de erro |
| Integrações | Contratos de pedido/resposta, mapping, autenticação, ownership, timeout/retry, correlação, duplicados, replay, indisponibilidade e reconciliação | Blueprint/interface; parâmetros delegados têm envelope |
| Segurança | Identidades/papéis, matriz de acesso, enforcement real, segregação, privilégios de serviço, auditoria e tratamento de dados | Blueprint A7 e FC; ocultar botão não substitui enforcement |
| Environments/ALM | Ambientes, soluções/componentes, configuração, referências de conexão, secrets refs, pipeline, promoção, rollback e responsabilidades | Blueprint A8 + trabalho; valores sensíveis fora do pacote |
| Capacidade/licenciamento | Volumes/picos, pressupostos, limites relevantes, entitlements necessários, fonte/data de verificação, custo e provas de capacidade | Blueprint/economia; não afirmar licença do tenant sem evidência |
| Migração/cutover | Mapping, limpeza, reconciliação, coexistência, ensaio, critérios go/no-go, rollback e destino do legado | Implementation-spec a partir da arquitetura A9; N/A justificado |
| Testes/provas | Unitários/funcionais, integração, permissões, falhas/recovery, capacidade aplicável, UAT e critério de entrada/saída | Trabalho e aceitação ligados a FC/provas; observado separado de planeado |
| Operação | Monitorização, alertas, suporte, ownership, incidentes, recuperação, manutenção e runbooks | Blueprint A10 + implementation-spec; responsabilidade identificada |
| Construção/backlog | Work packages, outputs, dependências, sequência, bloqueios, skills necessários e definition of done | Implementation-spec é autoridade; backlog é projeção |
| Estimativa | Esforço por inventário, método, pressupostos, incerteza, exclusões e revisão base | Estimate modo A; sem durações concorrentes na spec |

Ausência de um valor necessário é um gap, não convite para o modelo inventar defaults. Se a equipa puder decidir, a delegação inclui limites, impacto permitido, dono e teste. Se uma escolha alterar arquitetura/segurança/custo material autorizado, regressa à decisão.

## Rastreabilidade vertical

Cada jornada entregue permite seguir: requisito/regra → contrato funcional → dados/superfície/permissão/automação/integração aplicáveis → trabalho → aceitação/prova. Alguns elementos são partilhados entre jornadas; não duplicar trabalho ou estimativa por cada ligação.

Exemplo sintético: “submeter pedido sem duplicação” referencia FC de submissão, identidade estável do pedido, enforcement do papel, trigger de automação, política de idempotência, recuperação de integração, WP de construção e teste de repetição. Se não existir integração, a aresta é N/A justificada; não adicionar um sistema externo para completar o diagrama.

Validar ambos os sentidos: requisito sem trabalho/teste e trabalho sem motivo de desenho devem ser detetados. Trabalho técnico transversal pode referenciar obrigação arquitetural em vez de requisito funcional.

## Completude e níveis de entrega

- **Preliminar:** análise/desenho/estimativa condicional; claramente não pronto para build.
- **Pronto para revisão do destinatário:** scope e contrato completos, checks estruturais/semânticos requeridos concluídos, blockers de build resolvidos no âmbito.
- **Aceite pelo destinatário:** ato explícito de equipa/papel competente sobre revisão e âmbito, com condições.
- **Implementado/verificado:** só após execução e evidência dos testes correspondentes; não é consequência automática dos níveis anteriores.

Conservar níveis de prova V1–V4 e obrigações existentes conforme os seus contratos. O renderer não reclassifica prova nem declara uma prova realizada porque gerou o seu plano.

## Revisão de destinatário em contexto novo

Entregar apenas o pacote congelado. Pedir ao revisor/equipa:

1. Identificar o âmbito, exclusões e decisões autorizadas.
2. Preparar a ordem de construção a partir do inventário e dependências.
3. Explicar como implementaria uma jornada e um caminho de falha usando só o pacote.
4. Identificar dados, acessos, ambientes e decisões ainda necessários do cliente.
5. Definir como provaria aceitação e como operaria/recuperaria a solução.
6. Registar lacunas como `blocks_all`, `blocks_scope`, `delegated_choice` ou `implementation_proof`, com justificação.

Uma pergunta que obriga a redescobrir uma regra essencial é defeito de handoff. Uma pergunta sobre escolha delegada dentro de envelope pode ser trabalho normal de implementação. O autor responde através de nova revisão canónica; não resolver só num chat que o próximo destinatário não recebe.

## Critério de fecho

Zero lacunas essenciais não tratadas no âmbito entregue; nenhuma contradição material entre vistas; outputs íntegros e atuais; trabalho/testes/estimate rastreáveis; responsabilidades e autorizações presentes. Aceitação real registada separadamente. Se a equipa não estiver disponível, rotular revisão como simulada e manter essa limitação explícita.
