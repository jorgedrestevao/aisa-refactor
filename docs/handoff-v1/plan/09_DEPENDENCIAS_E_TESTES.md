# 09 — Seleção de dependências e refatorização da suite

## Regra normativa

Nenhum teste, módulo, agente, hook, formato, gate, ferramenta ou compromisso de compatibilidade é obrigatório só porque existia no projeto anterior. Preservar garantias necessárias ao objetivo atual; adaptar ou remover a implementação que deixou de as servir. Esta regra aplica-se a todas as fases e prevalece sobre interpretações de preservação integral do legado.

A refatorização continua a reutilizar kernel e pack úteis. Não é uma reescrita de raiz nem autorização para apagar dados, enfraquecer integridade ou remover testes apenas porque falham.

## F0: inventário com decisão por grupo

Produzir uma matriz com: grupo/componente, consumidores reais, requisito atual protegido, risco de remoção, custo de manutenção/execução, decisão, substituto se aplicável, fase responsável e critério de saída. Incluir testes parametrizados pelo comportamento que protegem; a contagem de casos não mede valor.

| Decisão | Quando usar | Evidência mínima |
| --- | --- | --- |
| Manter | Protege contrato necessário que continua válido | Requisito atual e cenário de falha |
| Adaptar | A garantia continua, mas a interface/comportamento mudou | Contrato novo e teste correspondente |
| Consolidar | Casos redundantes não acrescentam proteção | Mapeamento para cobertura mantida, incluindo limites relevantes |
| Isolar temporariamente | Consumidor real precisa do comportamento legado | Consumidor, âmbito, responsável e condição/data de retirada |
| Eliminar | Comportamento retirado, detalhe interno removido ou redundância demonstrada | Justificação e cobertura substituta, quando a garantia continua |

Exemplos: testes que exigem seis execuções de agentes devem ser substituídos por coverage das seis perspetivas; snapshots de prompts são removíveis se o texto exato não for contrato de um consumidor; crash recovery, conflitos, evidência e autorizações continuam a exigir proteção, mesmo que os testes sejam reescritos.

Não existe meta de 2000, 1000 ou 500 testes. Medir risco coberto, redundância, tempo de execução e manutenção. Os 46 cenários deste pacote são requisitos de cobertura: mapear para testes existentes e adicionar apenas lacunas. Um cenário pode precisar de vários testes e um teste pode cobrir vários cenários.

## Política de execução

- F0: inventariar toda a suite e executar os grupos relevantes para caracterizar os componentes reutilizados. Uma execução integral antiga é diagnóstico opcional quando útil e viável, não gate obrigatório nem dívida automática de correção.
- Desenvolvimento: testes dos componentes alterados e consumidores afetados.
- Fecho de fase: testes da fase, garantias críticas tocadas e regressões relacionadas.
- Antes de integração/release: suite completa aplicável à versão alvo, já reorganizada; compatibilidade apenas para consumidores explicitamente suportados.

Suite aplicável é definida pela matriz de requisitos/consumidores antes de observar resultados. Não excluir um teste a posteriori só para obter verde. Remoção/adaptação acompanha a mudança de contrato, com revisão e evidência no mesmo incremento.

## Compatibilidade sem obrigação permanente de classic

F0 decide se há consumidores/engagements que exigem execução classic dentro da nova versão. Sem necessidade demonstrada, não manter dois runtimes, agentes, hooks ou suites completos. Preservar a versão anterior numa referência git e dados acessíveis pode bastar; comparação com baseline pode executar essa versão isoladamente.

Quando necessária, a compatibilidade é limitada ao contrato realmente usado e tem condição de retirada. Pode ser um adaptador, importação ou exportação, em vez de runtime duplo. Engagement legado sem suporte de escrita é identificado e recusado com instrução clara; nunca reinterpretado automaticamente como handoff.

Proteção de dados e histórico é obrigatória mesmo quando suporte de execução termina. Não pressupõe construir migradores para formatos sem utilizadores. F7 implementa apenas os caminhos de migração identificados em F0; testa sempre rejeição segura de versões não suportadas.

## Gates e dívida antiga

Uma falha antiga só bloqueia se continuar presente e afetar um requisito da versão alvo ou consumidor suportado. Registar relação causal e teste/gate afetado. Backlogs, fases e NO-GO anteriores não são dependências automáticas.

O fecho de cada fase exige: decisões de disposição aplicadas, cobertura crítica preservada, testes novos/adaptados passando e remoções justificadas. A release não exige satisfazer comportamentos abandonados. Bugs fora do âmbito ficam documentados separadamente, sem serem ocultados como passes.
