# AISA — plano consolidado de refatorização e handoff

Versão do plano: 1.2 · Data: 2026-09-23 · Estado: especificação proposta, não implementada.

Baseline inspecionada: `jorgedrestevao/aisa`, branch `master`, commit `85baf1018ca2b238c41745f7f13dbb539589867f`.

## Resultado pretendido

Uma equipa deve conseguir receber um pacote AISA, perceber o que construir em Power Platform, implementar o âmbito autorizado, testar, colocar em produção e operar — sem reconstruir o raciocínio das sessões anteriores nem inventar decisões essenciais de negócio ou arquitetura.

O produto final não é uma promessa de que a solução já funciona. É um contrato de implementação rastreável, com decisões autorizadas, trabalho executável, provas a realizar e critérios de aceitação. A implementação, os testes reais e a aceitação humana continuam a ser atos distintos.

Em linguagem simples: compreender → desenhar → desafiar → decidir → especificar → entregar. Guardar o progresso a cada passo. Retomar sem adivinhar.

## Decisões deste plano

1. Preservar kernel, estados epistémicos, quatro fases, transações, grafo, blueprint, implementação e estimativa existentes.
2. Desenvolver `handoff-v1` de forma isolada até cumprir os gates de adoção. Manter execução `classic` na nova versão apenas se F0 identificar consumidores que a exijam, com âmbito e saída definidos.
3. Usar seis lentes como cobertura de análise, não como seis agentes obrigatórios.
4. Autorizar desenho funcional explícito antes do render. O render continua sem inventar solução.
5. Produzir candidatos comuns antes de os especialistas os reverem; selecionar especialistas por risco/pergunta material.
6. Dar conhecimento relevante do pack a autores e revisores, mantendo a separação research/craft.
7. Usar fontes e artefactos versionados como memória. Um resumo de sessão não é fonte de verdade.
8. Entregar vistas consistentes da mesma solução, com uma única autoridade para cada tipo de conteúdo.
9. Separar integridade, prontidão, autorização, aceitação do destinatário e prova de funcionamento.
10. Não evoluir extratores neste programa. Não reescrever o framework nem implementar a solução do cliente.

## Ordem de leitura

| Ficheiro | Utilização |
| --- | --- |
| [01_BASELINE.md](01_BASELINE.md) | O que existe, o que muda e onde |
| [02_CONTRATOS.md](02_CONTRATOS.md) | Autoridades, materialidade, rotas, readiness e desenho funcional |
| [03_AGENTES_E_PACK.md](03_AGENTES_E_PACK.md) | Lentes, especialistas, mandatos e revisão independente |
| [04_CONTINUIDADE.md](04_CONTINUIDADE.md) | Persistência, publicação, retoma, invalidação e recuperação |
| [05_FASES.md](05_FASES.md) | Sequência de implementação com gates e rollback |
| [06_VALIDACAO.md](06_VALIDACAO.md) | Testes automatizados, pilotos e aceitação |
| [07_MIGRACAO.md](07_MIGRACAO.md) | Compatibilidade, migração e rollout |
| [08_HANDOFF.md](08_HANDOFF.md) | Conteúdo completo de entrega e critérios do destinatário |
| [09_DEPENDENCIAS_E_TESTES.md](09_DEPENDENCIAS_E_TESTES.md) | Seleção do legado, racionalização da suite e compatibilidade limitada |
| [PROMPT_IMPLEMENTACAO.md](PROMPT_IMPLEMENTACAO.md) | Instrução de execução faseada para um agente de código |
| [templates/RELATORIO_FASE.md](templates/RELATORIO_FASE.md) | Registo de fecho e retoma de cada fase |

`examples/functional-contract.json` e `examples/work-checkpoint.json` são exemplos sintéticos dos contratos novos. Não são dados de cliente, schemas executáveis ou provas de uma implementação. Os schemas formais são entregáveis de F1/F2/F4.

Para verificar integridade estrutural do pacote: `python3 validate_package.py`. O ZIP inclui `MANIFEST.json` com hashes dos ficheiros. O validador verifica ficheiros, links relativos, exemplos JSON, dez fases e 46 IDs de testes especificados; não executa esses testes sobre o AISA.

## Precedência e limites

Este pacote substitui, como direção de trabalho, o anterior plano conceptual `AISA_Plano_Workflow_Kernel_Pack_Agentes.md`. Não substitui silenciosamente contratos em produção: a sua alteração é trabalho faseado, acompanhado por testes e migração. O plano de extratores fica separado e adiado.

Quando um contrato existente contradizer este plano, registar a alteração normativa em F1; não manter instruções contraditórias em simultâneo. Se a `master` avançar, fazer primeiro o delta contra o SHA fixado. Não assumir que esta inspeção valida commits posteriores.

Esta entrega é um plano baseado em inspeção de código e contratos. Não executa a refatorização nem certifica a suite. Não contém preços/licenças atuais: a confirmação desses dados pertence ao engagement, com fonte e data.

A F8 valida exclusivamente esta refatorização. Não exige concluir ou reexecutar fases do plano anterior, nem herda os seus estados de aprovação ou bloqueio. Testes existentes podem ser reutilizados quando relevantes; um problema anterior só bloqueia este programa se continuar presente e afetar um dos seus critérios de saída, com evidência registada.

Revisão 1.1: removidas referências ao piloto do plano anterior e explicitada a independência dos gates deste programa. Mantidas as dez fases e os 46 cenários de validação.

Revisão 1.2: preservação de cobertura em vez de preservação integral da suite; triagem de testes e dependências em F0; classic e migração limitados a necessidades demonstradas. Não há obrigação de manter os 2000+ testes ou satisfazer comportamentos abandonados.

## Política de implementação

Incrementos pequenos, perfil opt-in e primeiro percurso vertical antes de expandir. Cada fase termina com testes, artefactos persistidos, riscos conhecidos e uma decisão explícita de continuar. Sem push, deploy, migração destrutiva ou aprovação de cliente implícitos.
