# -*- coding: utf-8 -*-
"""handoff-v1 F4.5 — o render lê os contratos funcionais e não inventa o que falta.

Desenho: `docs/handoff-v1/F4/DESENHO.md` §5 (Q4). Motor: `functional.py render-gate`.

    T23  o render encontra um detalhe funcional em falta → não inventa; devolve a lacuna ao
         autor funcional (`owner: functional`)
    gate do render: referência e aprovação desactualizadas bloqueiam a publicação final
"""
import json
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
AU = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_functional_authorization.py"))
FC = AU["FC"]
F = AU["F"]
R = AU["R"]
DOC = "## 6. Comportamento\n\nA submissão segue FC-0001 (contrato funcional).\n"


def approve_blueprint(eng, version="01", did=None):
    d = R["draft"](eng, ["decisions.md"])
    p = eng / "_drafts" / d["draft"] / "decisions.md"
    texto = p.read_text(encoding="utf-8")
    n = did or "D-{:03d}".format(len([l for l in texto.splitlines() if l.startswith("## D-")]) + 1)
    p.write_text(texto + "\n## {} — Blueprint bp-v{} aprovado\n\n- **Validated by**: owner "
                 "(dados de teste)\n- **Timestamp**: 2026-09-23T23:00:00Z\n".format(n, version),
                 encoding="utf-8", newline="\n")
    R["publish"](eng, d["draft"])


def ready(tmp):
    """FC-0001 completo, autorizado, sobre o desenho v01 aprovado."""
    eng = AU["engagement"](tmp)
    approve_blueprint(eng)
    AU["publish"](eng, [AU["fc_idempotencia"]()], 1)
    AU["authorize"](eng, ["FC-0001"])
    return eng


class PortaoFinal(unittest.TestCase):

    def test_an_authorised_current_contract_on_the_approved_blueprint_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = ready(tmp)
            g = F["render_gate"](eng, text=DOC)
            self.assertTrue(g["final_allowed"], g)
            self.assertEqual(g["cited"], ["FC-0001"])
            self.assertEqual(g["approved_blueprint"], "_blueprint/ux-blueprint_v01.yaml")

    def test_a_stale_authorisation_blocks_the_final_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = ready(tmp)
            AU["publish"](eng, [AU["fc_idempotencia"](rule="outra regra")], 2)
            g = F["render_gate"](eng, text=DOC)
            self.assertFalse(g["final_allowed"])
            self.assertIn("AUTHORIZATION_STALE", [b["code"] for b in g["blocked"]])

    def test_a_contract_on_a_blueprint_that_is_not_the_approved_one_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = ready(tmp)
            v1 = (eng / "_blueprint" / "ux-blueprint_v01.yaml").read_text(encoding="utf-8")
            (eng / "_blueprint" / "ux-blueprint_v02.yaml").write_text(
                v1.replace("version: v01", "version: v02"), encoding="utf-8")
            approve_blueprint(eng, "02")
            g = F["render_gate"](eng, text=DOC)
            self.assertFalse(g["final_allowed"])
            self.assertIn("STALE_REFERENCE", [b["code"] for b in g["blocked"]])

    def test_no_approved_blueprint_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = AU["engagement"](tmp)
            AU["publish"](eng, [AU["fc_idempotencia"]()], 1)
            AU["authorize"](eng, ["FC-0001"])
            g = F["render_gate"](eng, text=DOC)
            self.assertIn("NO_APPROVED_BLUEPRINT", [b["code"] for b in g["blocked"]])


class T23_NaoInventa(unittest.TestCase):

    def test_a_missing_detail_goes_back_to_the_functional_author(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = AU["engagement"](tmp)
            approve_blueprint(eng)
            AU["publish"](eng, [AU["fc_idempotencia"](acceptance_examples=[])], 1)
            g = F["render_gate"](eng, text=DOC)
            self.assertFalse(g["final_allowed"])
            gap = [x for x in g["gaps"] if x["fc"] == "FC-0001"]
            self.assertTrue(gap)
            self.assertEqual({x["owner"] for x in gap}, {"functional"})
            self.assertIn("MISSING_ACCEPTANCE_EXAMPLES", [x["code"] for x in gap])

    def test_a_cited_contract_that_does_not_exist_is_a_gap_not_a_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = ready(tmp)
            g = F["render_gate"](eng, text=DOC + "E também FC-0009.\n")
            self.assertIn("MISSING_CONTRACT", [x["code"] for x in g["gaps"]])
            self.assertFalse(g["final_allowed"])

    def test_the_render_contract_names_the_functional_owner(self):
        rc = (ROOT / "library" / "kernel" / "render-contract.md").read_text(encoding="utf-8")
        sk = (ROOT / ".claude" / "skills" / "aisa-render" / "SKILL.md").read_text(encoding="utf-8")
        tp = (ROOT / "library" / "packs" / "pp" / "deliverable-templates" /
              "implementation-spec.template.md").read_text(encoding="utf-8")
        for t in (rc, sk):
            self.assertIn("| estimate | evidence | functional }", t)
        self.assertIn("7b. **Functional gate — before a real version**", sk)
        self.assertIn("Never write the missing value to make the gate pass", sk)
        self.assertIn("_design/functional-contracts.json — behaviour", tp)


class CLI(unittest.TestCase):

    def test_render_gate_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = ready(tmp)
            (eng / "prev.md").write_text(DOC, encoding="utf-8")
            (eng / "mau.md").write_text(DOC + "FC-0009\n", encoding="utf-8")
            for f, rc in (("prev.md", 0), ("mau.md", 4)):
                p = subprocess.run([sys.executable, str(TOOLS / "functional.py"), "render-gate",
                                    "--engagement", str(eng), "--file", f],
                                   capture_output=True, text=True, timeout=300,
                                   env=dict(os.environ, PYTHONIOENCODING="utf-8"))
                self.assertEqual(p.returncode, rc, p.stdout + p.stderr)
                self.assertIn("final_allowed", json.loads(p.stdout))


if __name__ == "__main__":
    unittest.main()
