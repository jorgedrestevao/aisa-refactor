# 04 — Conhecimento persistente e continuidade de sessão

## Objetivo e limite

Uma sessão nova deve saber o que foi estabelecido, autorizado, alterado, ainda não integrado e o próximo trabalho seguro. Não deve precisar da conversa anterior. Isso não permite recuperar palavras nunca persistidas: se a sessão terminar antes da primeira captura, pedir reenvio, sem reconstruir por adivinhação.

Guardar rationale conciso, evidência, alternativas e condições de revisita; não guardar raciocínio interno privado nem transcrições extensas como substituto de estrutura.

## Reutilizar o que existe

`bootstrap.py` continua a produzir contexto consistente. `operation.py` continua a publicar. `graph.py`/`resolve.py` continuam a controlar referências e espelho da SU. `coverage.py` continua a decidir freshness semântica. O módulo de workflow apenas liga tarefa, inputs e next action a estes mecanismos.

O novo checkpoint não replica SU, decisões ou blueprint. Guarda referências e estado de trabalho. O índice de handoff também não se torna um sétimo registo de decisões.

## Checkpoint mínimo

O ficheiro `_work/checkpoint.json` contém:

- Versão de schema, engagement, revisão, perfil e rota.
- Objetivo corrente, âmbito e referências às autorizações.
- Tarefas com papel, inputs versionados, estado, dependências e critérios de fecho.
- Resultados recebidos mas não integrados, com localização/hash e razão.
- Blockers ligados aos IDs canónicos, sem copiar o seu conteúdo mutável.
- Última operação integrada e próximo passo proposto, incluindo por que é seguro.

Separar `active_task` de `next_actions`: pode haver mais de uma tarefa pronta, mas não assumir execução paralela sem disponibilidade e autorização do ambiente. O plano não exige um serviço de agentes em background.

## Protocolo de publicação

1. Bootstrap lê autoridades e devolve snapshot/read-set coerente, com hashes dos bytes e revisões semânticas.
2. Tarefa declara qualquer input adicional antes de o usar: contrato funcional, blueprint, spec, unidade do pack ou fonte específica.
3. Autor produz resultado draft fora das autoridades; registar versão base.
4. Receção verifica schema, referências, âmbito, autorização aplicável e freshness. Um resultado recebido ainda não conta como integrado.
5. Coordenador constrói um único plano de mutação: deltas de autoridades, espelho/dependências e checkpoint correspondentes.
6. Antes de publicar, validar todo o read-set esperado. Inputs alterados → `STALE_INPUT`, manter draft e pedir rebase/revisão. Nunca last-writer-wins silencioso.
7. Publicar pelo protocolo existente com recuperação determinística; atualizar pointer/receipt apenas conforme contrato do coordenador.
8. Após sucesso, outputs integrados tornam-se visíveis para readiness e projeções. Render não consome drafts.

Não exigir atomicidade física de múltiplos ficheiros se o sistema de ficheiros não a fornece. Exigir atomicidade observável: leitores aceitam a revisão anterior consistente ou a nova consistente, ou recebem `RECOVERY_REQUIRED`; nunca um conjunto misto apresentado como atual.

O read-set inclui inputs efetivamente consumidos e dependências necessárias à decisão. Não incluir receipts/logs transitórios como inputs recursivos do próprio digest. Normalizar hashing e campos excluídos em schema; preservar hash de bytes para integridade e fingerprint semântico para invalidação. Mudança editorial pode dispensar revisão semântica, mas a release continua identificando os bytes exatos publicados.

## Escritas e hooks

No perfil novo, mutações canónicas passam pelo coordenador. Hooks de escrita são guardas, deteção/reparação compatível e diagnóstico, não uma segunda implementação da transação. O comportamento atual de espelhar a SU depois de Edit/Write não prova atomicidade SU+grafo.

Se um utilizador editar diretamente uma autoridade: detetar divergência, preservar a edição, impedir publicação inconsistente e propor reconciliação explícita. Não apagar a alteração nem declarar que a escrita nunca aconteceu. No classic, preservar os fluxos suportados e tornar limitações visíveis.

## Eventos de checkpoint

Persistir quando: uma fonte/resposta é capturada, uma questão muda materialmente, um mandato começa, um resultado chega, uma integração termina, uma decisão é autorizada, uma revisão fica stale, um gate muda ou um handoff é publicado.

Checkpoint antes de trabalho demorado identifica tarefa em curso; checkpoint de resultado permite retomar sem repetir chamada. Após crash, `running` não significa que continua a executar: reconciliar execução/resultados e converter em retomável/bloqueada antes de relançar. Usar idempotency key da operação para evitar integração duplicada.

## Retoma a frio

1. Resolver engagement/perfil e verificar versões suportadas.
2. Ler checkpoint e snapshot consistente; executar diagnóstico de recuperação pendente.
3. Reconciliar tarefas e resultados não integrados; não os promover automaticamente.
4. Calcular freshness e raio de impacto de alterações desde o snapshot.
5. Selecionar contexto mínimo: objetivo, âmbito, decisões aplicáveis, blockers críticos, inputs da próxima tarefa e dependências relevantes.
6. Informar claramente o que ficou fora do orçamento. Se faltar contexto necessário, carregar mais ou dividir tarefa; não resumir o blocker para fora do contexto.
7. Apresentar próximo passo fundamentado e continuar só dentro da autorização corrente.

O orçamento atual de contexto do bootstrap pode ser ponto de partida, não teto que autoriza trabalho incompleto. Testar oversize: críticos primeiro e estado parcial explícito. Um digest de sessão é apenas uma projeção regenerável do checkpoint e das autoridades.

## Invalidação

Dependências tipadas: `supports`, `constrains`, `implements`, `verifies`, `estimates`, `derived_from`. Reutilizar tipos equivalentes já existentes, com migração se necessário.

Mudança numa premissa → alegações/decisões dependentes potencialmente stale → FC/blueprint afetados → trabalho/testes/estimate → outputs de handoff. Não invalidar tudo sem razão nem manter outputs a verde porque os filenames não mudaram.

O motor marca necessidade de reavaliação, não decide sozinho que a nova evidência confirma/refuta. Revisor pode registar “sem impacto semântico” com referência à mudança. Quando uma decisão é revista, preservar decisão anterior e motivo de substituição.

## Falhas a suportar

| Ponto de falha | Comportamento obrigatório |
| --- | --- |
| Antes da captura | Nenhuma garantia de persistência; pedir informação novamente |
| Depois do draft, antes da integração | Resultado recuperável, não canónico |
| A meio da operação | Leitura bloqueada/consistente; recuperação idempotente comprovada |
| Depois de publicar, antes da resposta ao utilizador | Receipt permite reconhecer sucesso sem duplicar |
| Duas sessões com a mesma revisão base | Uma publica; a outra recebe conflito e reavalia |
| Resultado de especialista chega tarde | Guardar como recebido/stale, nunca integrar como atual |
| Schema futuro desconhecido | Falhar com mensagem e caminho de compatibilidade; não descartar campos |
| Falta de fonte referenciada | Evidência indisponível explícita, blockers recalculados |

## Segurança e retenção

Não guardar tokens, credenciais ou segredos em checkpoints, logs ou pacotes. Guardar referência segura/configuração requerida, não o valor. Evitar duplicar dados pessoais em snippets; manter localização e mínimo necessário. Política de retenção/redação pertence ao engagement e tem de abranger artefactos derivados e drafts, preservando a rastreabilidade permitida.

Retoma noutro ambiente exige os artefactos referenciados acessíveis e permissões adequadas. Persistir no repositório não resolve por si só backup, acesso, sincronização ou requisitos de residência dos dados; documentar estas responsabilidades no setup operacional.
