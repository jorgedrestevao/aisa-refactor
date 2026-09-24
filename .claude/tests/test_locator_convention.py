# -*- coding: utf-8 -*-
"""handoff-v1 F6.3 (S6) — a contagem dos `¶` num `.md` é a do extractor.

`library/kernel/states.md` → *Confirmed threshold*: em `.md`, `¶n` é a n-ésima linha não
vazia que não é título nem linha de tabela, a contar do topo — o `[¶n]` que
`text_extract.py` escreve. As fixtures do handoff-v1 citam as suas fontes assim; uma
citação que aponta um parágrafo que não existe é defeito da fixture (o 1.º ensaio T43
encontrou-o: `../docs/handoff-v1/F5/T43-ENSAIO.md` L-15)."""
import re
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "text_extract.py"))
FIX = ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1"
CIT = re.compile(r"\b([\w-]+\.md)#¶(\d+)")
TESTES = ["test_hv1_02_discovery.py", "test_functional_authorization.py",
          "test_hv1_design_path.py", "test_hv1_vertical.py", "test_review_candidates.py",
          "test_trace.py", "test_hv1_release_paths.py"]


def paragrafos(path):
    body, _u, _s, _r = T["extract_md"](str(path))
    return {int(m.group(1)) for l in body for m in [re.match(r"\[¶(\d+)\]", l)] if m}


class Convencao(unittest.TestCase):

    def test_the_kernel_states_the_rule(self):
        s = (ROOT / "library" / "kernel" / "states.md").read_text(encoding="utf-8")
        self.assertIn("exactly the number `text_extract.py` writes as `[¶n]`", s)

    def test_every_fixture_citation_points_at_an_existing_paragraph(self):
        # Dois `pedido.md` (fx-hv1-02 e fx-hv1-04): a citação tem de existir numa das fontes
        # com esse nome — limite declarado; a fixture certa é a do teste que a cita.
        fontes = {}
        for p in FIX.glob("*/sources/*.md"):
            fontes.setdefault(p.name, set()).update(paragrafos(p))
        falhas, vistas = [], 0
        for t in TESTES:
            for nome, n in CIT.findall((ROOT / ".claude" / "tests" / t).read_text(
                    encoding="utf-8")):
                if nome in fontes:
                    vistas += 1
                    if int(n) not in fontes[nome]:
                        falhas.append("{}: {}#¶{}".format(t, nome, n))
        self.assertEqual(falhas, [])
        self.assertGreater(vistas, 12, "o teste não conferiu citações")

    def test_the_rule_is_the_one_the_fixture_su_relies_on(self):
        p = FIX / "fx-hv1-02-pp-constrained" / "sources" / "matriz-papeis.md"
        body, _u, _s, _r = T["extract_md"](str(p))
        linha = next(l for l in body if l.startswith("[¶2]"))
        self.assertIn("nunca aprova", linha, "C-004 cita matriz-papeis.md#¶2")


if __name__ == "__main__":
    unittest.main()
