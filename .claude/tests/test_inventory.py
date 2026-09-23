# -*- coding: utf-8 -*-
"""handoff-v1 F6.1 — o âmbito autorizado e o inventário de trabalho, pelo coordenador.

Desenho: `docs/handoff-v1/F6/DESENHO.md` §1 (Q1, Q3).

    âmbito      `SCOPE-NNNN` com incluídos que resolvem (SU, jornadas de FC) e exclusões
                sempre autorizadas por um `D-NNN` que existe (T33, parte do motor)
    inventário  `WP-NNNN` com o que realiza (FC, nós do desenho pelo resolvedor do coverage,
                um nó exacto), provas que são obrigações de prova, dependências sem ciclo,
                aceitação ligada a FC que existem; nunca esforço (Q2)
    publicação  uma operação do coordenador, revisão + cópia imutável; ids nunca reutilizados;
                base ou inputs mudados → `STALE_INPUT`; repetir a publicação devolve o recibo
"""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
VT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_hv1_vertical.py"))
INV = runpy.run_path(str(TOOLS / "inventory.py"))
BP = "_blueprint/ux-blueprint_v01.yaml"
NO = BP + "#architecture/compositions[component=submissao-idempotente]"


def engagement(tmp):
    eng, _c, _r = VT["percurso"](tmp)
    return eng


def escopo(eng, revision=1, **over):
    s = {"id": "SCOPE-0001", "name": "Pedido, aprovação e passagem a compras",
         "includes": [{"ref": "C-001", "reason": "o âmbito declarado"},
                      {"ref": "J-0001", "reason": "submissão"},
                      {"ref": "J-0003", "reason": "aprovação com segregação"}],
         "excludes": [{"ref": "FC-0002", "reason": "arredondamento por escolher (U-001)",
                       "authorization_ref": "decisions.md#D-004"}],
         "authorized_by": "D-004"}
    s.update(over)
    return {"schema_version": "handoff-scope/1", "engagement_id": eng.name,
            "revision": revision, "based_on": [{"ref": "shared-understanding.md"}],
            "retired_ids": [], "items": [s]}


def wp(wid="WP-0001", **over):
    w = {"id": wid, "scope_id": "SCOPE-0001", "purpose": "Submissão idempotente",
         "realizes": ["FC-0001", NO], "proves": [], "depends_on": [],
         "acceptance": [{"fc": "FC-0001", "condition": "exemplo negativo do FC-0001"}],
         "skills": ["plataforma"], "definition_of_done": "exemplos do FC-0001 a passar"}
    w.update(over)
    return w


def inventario(eng, items, revision=1, **extra):
    d = {"schema_version": "handoff-work-packages/1", "engagement_id": eng.name,
         "revision": revision, "based_on": [{"ref": "_design/functional-contracts.json"}],
         "retired_ids": [], "items": items}
    d.update(extra)
    return d


def publish(eng, kind, data):
    dr = INV["draft"](eng, kind)
    Path(dr["path"]).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return INV["publish"](eng, dr["draft"])


def refused(test, eng, kind, data, code):
    with test.assertRaises(INV["InventoryError"]) as err:
        publish(eng, kind, data)
    test.assertEqual(err.exception.code, "INTEGRITY_FAILURE")
    test.assertIn(code, [p["code"] for p in err.exception.detail["problems"]])


class Ambito(unittest.TestCase):

    def test_published_with_history_and_authorised_exclusions(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            r = publish(eng, "scope", escopo(eng))
            self.assertEqual(r["gaps"], [])
            self.assertTrue((eng / "_design/history/scope.r0001.json").is_file())
            self.assertEqual(INV["show"](eng, "scope")["items"], ["SCOPE-0001"])

    def test_t33_an_exclusion_without_authorisation_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            refused(self, eng, "scope", escopo(eng, excludes=[
                {"ref": "passagem a compras", "reason": "fica para depois",
                 "authorization_ref": "D-099"}]), "UNAUTHORIZED_EXCLUSION")

    def test_an_include_must_resolve(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            refused(self, eng, "scope", escopo(eng, includes=[
                {"ref": "C-999", "reason": "x"}]), "DEAD_REF")
            refused(self, eng, "scope", escopo(eng, includes=[
                {"ref": "J-0099", "reason": "jornada sem FC"}]), "DEAD_REF")

    def test_an_unauthorised_scope_is_a_visible_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            r = publish(eng, "scope", escopo(eng, authorized_by=None))
            self.assertIn("SCOPE_NOT_AUTHORIZED", [g["code"] for g in r["gaps"]])


class Inventario(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.eng = engagement(self.tmp.name)
        publish(self.eng, "scope", escopo(self.eng))

    def tearDown(self):
        self.tmp.cleanup()

    def test_published_with_design_nodes_resolved(self):
        r = publish(self.eng, "work-packages", inventario(self.eng, [
            wp(), wp("WP-0002", purpose="Aprovação com segregação no servidor",
                     realizes=["FC-0003", "C-004"], depends_on=["WP-0001"],
                     acceptance=[{"fc": "FC-0003", "condition": "exemplo negativo"}])]))
        self.assertEqual(r["gaps"], [])
        self.assertTrue((self.eng / "_design/history/work-packages.r0001.json").is_file())

    def test_a_design_reference_resolves_to_exactly_one_node(self):
        refused(self, self.eng, "work-packages", inventario(self.eng, [
            wp(realizes=[BP + "#architecture/compositions[component=nao-existe]"])]),
            "DEAD_REF")

    def test_proves_points_at_a_proof_obligation(self):
        refused(self, self.eng, "work-packages", inventario(self.eng, [wp(proves=[NO])]),
                "NOT_A_PROOF")

    def test_dependencies_resolve_and_do_not_cycle(self):
        refused(self, self.eng, "work-packages", inventario(self.eng, [
            wp(depends_on=["WP-0009"])]), "DEAD_REF")
        refused(self, self.eng, "work-packages", inventario(self.eng, [
            wp(depends_on=["WP-0002"]), wp("WP-0002", depends_on=["WP-0001"])]),
            "DEPENDENCY_CYCLE")

    def test_q2_the_inventory_never_carries_effort(self):
        refused(self, self.eng, "work-packages", inventario(self.eng, [
            wp(effort="5 dias")]), "EFFORT_IN_INVENTORY")

    def test_the_scope_and_the_contracts_must_exist(self):
        refused(self, self.eng, "work-packages", inventario(self.eng, [
            wp(scope_id="SCOPE-0009")]), "DEAD_REF")
        refused(self, self.eng, "work-packages", inventario(self.eng, [
            wp(acceptance=[{"fc": "FC-0099", "condition": "x"}])]), "DEAD_REF")

    def test_missing_acceptance_is_a_visible_gap_not_a_refusal(self):
        r = publish(self.eng, "work-packages", inventario(self.eng, [wp(acceptance=[])]))
        self.assertIn("MISSING_ACCEPTANCE", [g["code"] for g in r["gaps"]])

    def test_ids_are_never_reused(self):
        publish(self.eng, "work-packages", inventario(self.eng, [wp(), wp("WP-0002")]))
        refused(self, self.eng, "work-packages", inventario(self.eng, [wp()], 2),
                "SILENT_REMOVAL")
        refused(self, self.eng, "work-packages",
                inventario(self.eng, [wp(), wp("WP-0002")], 2, retired_ids=["WP-0002"]),
                "REUSED_ID")

    def test_a_changed_input_after_the_draft_is_stale_and_replay_returns_the_receipt(self):
        dr = INV["draft"](self.eng, "work-packages")
        Path(dr["path"]).write_text(json.dumps(inventario(self.eng, [wp()])), encoding="utf-8")
        su = self.eng / "shared-understanding.md"
        antes = su.read_text(encoding="utf-8")
        su.write_text(antes + "\n", encoding="utf-8")
        with self.assertRaises(INV["InventoryError"]) as err:
            INV["publish"](self.eng, dr["draft"])
        self.assertEqual(err.exception.code, "STALE_INPUT")
        su.write_text(antes, encoding="utf-8")
        r1 = INV["publish"](self.eng, dr["draft"])
        self.assertTrue(INV["publish"](self.eng, dr["draft"])["replayed"])
        self.assertEqual(r1["revision"], 1)


if __name__ == "__main__":
    unittest.main()
