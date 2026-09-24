# -*- coding: utf-8 -*-
"""handoff-v1 F4.3 — o desenho e o contrato funcional não dizem duas coisas da mesma regra.

Desenho: `docs/handoff-v1/F4/DESENHO.md` §3 (Q6).

    T21  blueprint e FC contradizem a mesma regra → conflito visível; nenhum lado escolhido
         em silêncio; o FC afectado não é autorizável, e a versão do desenho em aprovação é
         comparada com os FC correntes (`functional.py conflicts --blueprint`)
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
FC = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_functional_contracts.py"))
F = FC["F"]
OWNER = "owner (responsável de compras, dados de teste — via AskUserQuestion)"


def estado(**campo):
    base = {"field_ref": "pedidos.estado", "required": True,
            "values": ["submetido", "aprovado", "rejeitado"]}
    base.update(campo)
    return base


def item(*inputs):
    return FC["fc_submissao"](inputs=[{"field_ref": "pedidos.chave_submissao",
                                       "required": True}] + list(inputs))


def publish(eng, it, revision=1):
    return F["publish"](eng, FC["write_draft"](eng, FC["contracts"](eng, [it], revision)))


class T21_Contradicao(unittest.TestCase):

    def test_each_facet_that_diverges_is_a_visible_conflict(self):
        casos = {"values": estado(values=["submetido", "aprovado"]),
                 "required": estado(required=False),
                 "type": estado(type="text"),
                 "default": dict(estado(), default="aprovado")}
        for facet, inp in casos.items():
            with self.subTest(facet=facet):
                with tempfile.TemporaryDirectory() as tmp:
                    eng = FC["engagement"](tmp)
                    if facet == "default":
                        bp = eng / "_blueprint" / "ux-blueprint_v01.yaml"
                        bp.write_text(bp.read_text(encoding="utf-8").replace(
                            "values: [submetido, aprovado, rejeitado],",
                            "values: [submetido, aprovado, rejeitado], default: submetido,"),
                            encoding="utf-8")
                    r = publish(eng, item(inp))
                    self.assertEqual(r["code"], "BLOCKING_GAP")
                    c = F["show"](eng)["items"]["FC-0001"]
                    self.assertEqual([x["facet"] for x in c["conflicts"]], [facet])
                    self.assertFalse(c["authorizable"])
                    x = c["conflicts"][0]
                    self.assertEqual(x["code"], "FC_BLUEPRINT_CONFLICT")
                    self.assertTrue(x["blueprint"]["ref"].startswith("_blueprint/"))
                    self.assertIn("FC-0001", x["functional"]["ref"])

    def test_a_conflicted_contract_is_not_authorized(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = FC["engagement"](tmp)
            publish(eng, item(estado(required=False)))
            with self.assertRaises(F["FunctionalError"]) as err:
                F["authorization_block"](eng, ["FC-0001"], OWNER, "SCOPE-0001")
            self.assertEqual(err.exception.code, "BLOCKING_GAP")
            self.assertIn("contradiz o desenho", str(err.exception))

    def test_what_only_one_side_declares_is_not_a_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = FC["engagement"](tmp)
            inp = {"field_ref": "pedidos.estado", "required": True, "default": "submetido"}
            publish(eng, item(inp))
            self.assertEqual(F["show"](eng)["items"]["FC-0001"]["conflicts"], [])

    def test_the_order_of_allowed_values_is_not_a_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = FC["engagement"](tmp)
            publish(eng, item(estado(values=["rejeitado", "submetido", "aprovado"])))
            self.assertEqual(F["show"](eng)["items"]["FC-0001"]["conflicts"], [])

    def test_reconciling_clears_the_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = FC["engagement"](tmp)
            publish(eng, item(estado(required=False)))
            publish(eng, item(estado()), revision=2)
            c = F["show"](eng)["items"]["FC-0001"]
            self.assertEqual(c["conflicts"], [])
            self.assertTrue(c["authorizable"])


class DesenhoEmAprovacao(unittest.TestCase):
    """Uma versão nova do desenho é comparada com os FC correntes antes de ir ao dono."""

    def test_a_new_blueprint_version_that_contradicts_a_contract_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = FC["engagement"](tmp)
            publish(eng, item(estado()))
            v1 = (eng / "_blueprint" / "ux-blueprint_v01.yaml").read_text(encoding="utf-8")
            (eng / "_blueprint" / "ux-blueprint_v02.yaml").write_text(
                v1.replace("version: v01", "version: v02").replace(
                    "values: [submetido, aprovado, rejeitado]",
                    "values: [submetido, aprovado, rejeitado, cancelado]"), encoding="utf-8")
            self.assertEqual(F["conflicts"](eng), [], "a versão de based_on não diverge")
            novo = F["conflicts"](eng, blueprint="_blueprint/ux-blueprint_v02.yaml")
            self.assertEqual([c["facet"] for c in novo], ["values"])
            p = subprocess.run(
                [sys.executable, str(TOOLS / "functional.py"), "conflicts", "--engagement",
                 str(eng), "--blueprint", "_blueprint/ux-blueprint_v02.yaml"],
                capture_output=True, text=True, timeout=300,
                env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
            self.assertEqual(len(json.loads(p.stdout)["conflicts"]), 1)


if __name__ == "__main__":
    unittest.main()
