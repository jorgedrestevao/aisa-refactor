# Fixtures handoff-v1 (F0)

Dados 100% sintéticos. Nenhuma organização, pessoa, valor ou sistema aqui existe: `Organização Exemplo` e `ERP-X` são nomes inventados para teste. Não copiar para cá material de engagements reais.

Cada pasta `fx-hv1-NN-*` é um *source pack*, com dois elementos:
- `scenario.json`: âmbito, rota, restrições e resultados esperados;
- `sources/`: as fontes que um engagement receberia.

Os resultados esperados descrevem conhecimento, decisão e rastreabilidade, e citam os IDs de cenário de `docs/handoff-v1/plan/06_VALIDACAO.md`. Não fixam texto de output.

As âncoras `[X1]` nas fontes são os pontos que `source_refs` cita (`<ficheiro>#X1`). Mudar uma fonte obriga a rever os `expected` que a citam.

| Pasta | Rota / caso | Cenário de 06_VALIDACAO |
| --- | --- | --- |
| `fx-hv1-01-solution-choice` | `solution-choice` | 1 — escolha de solução |
| `fx-hv1-02-pp-constrained` | `platform-constrained` | 2 — PP constrained |
| `fx-hv1-03-change-impact` | `change-impact`, sobre a 02 | 3 — change-impact |
| `fx-hv1-04-headless` | `platform-constrained`, headless | 4 — headless |
| `fx-hv1-05-migration` | `platform-constrained`, migração | 5 — substituição/migração |

O registo completo, incluindo as fixtures existentes reutilizadas e as que ficam fora, está em `docs/handoff-v1/F0/fixture-registry.json`.

Em F0 estas fixtures são só dados. Os testes que as executam nascem com o perfil novo (F1 em diante). `.claude/tests/test_handoff_f0.py` valida apenas a estrutura, a proveniência e as referências.
