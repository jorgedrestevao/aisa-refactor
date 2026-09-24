## R-01 — data

**What matters.** A verdade dos preços vive hoje no ERP-X; a folha de compras guarda uma cópia manual, actualizada "quando alguém se lembra" (C-004) — risco de desactualização já observado (R-002). O valor do pedido segue uma fórmula conhecida — quantidade × preço unitário por linha, mais IVA (C-005) — mas o ponto de arredondamento não está definido e já causou diferenças reais com a contabilidade: **isto é o próprio mecanismo de consistência que a questão central desta lente pergunta ("como é que fica consistente?"), não uma escolha de desenho a jusante** (correcção pós-revisão independente) — por isso esta perspectiva fica `gap`, a rotear para U-003, e não `assessed`. Não existe hoje um sistema único de registo dos pedidos: vivem dispersos entre email e folha de cálculo (A-003). Retenção de 10 anos para documentos de compra já está Confirmed via enquadramento (M-4).

**Tensions / risks.** A decisão de manter ou não uma cópia própria dos preços (U-004) é estrutural — muda o modelo de dados e se há dependência de integração com o ERP-X. Sensibilidade dos dados: nada de especialmente sensível para além de custo e identidade do requerente; nenhuma classificação adicional foi declarada, e nenhum sinal aponta para tal — não escrito como pergunta.

**Open evidence.**
- `Inputs catalog` — MAP → R-002.
- `chain: linhas do pedido → valor do pedido` — MAP → C-005.
- `Exceptions catalogo-desactualizado` — MAP → R-002.
- `documentos de compra conservados 10 anos` (M-4) — MAP → M-4.
- `Structural constraints catalogo` — ADOPT → U-004.
- PM-U-001 (arredondamento) — ADOPT → U-003.
- PM-U-003 (ERP-X tempo-real vs cópia) — ADOPT → U-004.

## R-02 — data

**What matters.** Sem fontes novas desde R-01. Reconfirmo: verdade dos preços no ERP-X hoje (C-004), fórmula do valor do pedido conhecida (C-005), arredondamento já resolvido por resposta do dono em R-01 (U-003 → C-007), estrutura de dados do catálogo por decidir (U-004). Nenhuma fonte nova classifica sensibilidade ou traz um entity novo.

**Tensions / risks.** Sem alteração face a R-01.

**Open evidence.** (none — nada de novo por dispor.)
