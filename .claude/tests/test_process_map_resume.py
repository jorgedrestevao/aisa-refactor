"""process-map M4 — a retoma recupera o processo, a actualidade é proporcional e o
dashboard mostra o mapa.

Casos (docs/process-map/PLANO.md §15): MAP-23 (retoma sem conversa: o mapa entra no
resumo da retoma a partir dos bytes que o snapshot validou; orçamento excedido → parcial,
com o que ficou de fora e como expandir, e os bloqueios nunca truncados), MAP-22 (fonte
alterada: mudança editorial com revalidação registada mantém a validação; mudança material
pede revisão dos elementos afectados e nova validação; um digest trocado sem registo nunca
volta a «actual»), MAP-24 (mesmos inputs → mesmo SVG e mesmo modelo do dashboard), mapa
ausente, SU antiga, pendência por recuperar, e o separador Mapa do dashboard.

    python .claude/tests/test_process_map_resume.py
"""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
CORE = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_process_map_core.py"),
                      run_name="helpers")
P = CORE["P"]
W = runpy.run_path(str(TOOLS / "workflow.py"))
D = runpy.run_path(str(TOOLS / "dashboard.py"))
OWNER = "owner (Responsável de Pricing, via AskUserQuestion)"


class Base(CORE["Base"]):

    def published(self, draft=None):
        d = self.stamped(draft)
        r = self.publish(d)
        self.assertTrue(r["published"], r.get("verdict"))
        return r

    def validate(self):
        p = self.eng / "decisions.md"
        p.write_text(p.read_text(encoding="utf-8") + P["approval_block"](
            self.eng, "processo diário", "MAPG-001 por esclarecer", OWNER,
            "2026-09-25T10:00:00Z"), encoding="utf-8")

    def publish_draft(self, d):
        p = self.save(d, "reval.json")
        r = P["publish"](self.eng, d, p)
        self.assertTrue(r["published"], r.get("verdict"))
        return r


class MAP23_Retoma(Base):

    def test_the_resume_carries_the_map_from_the_bytes_it_validated(self):
        self.published()
        r = W["resume"](self.eng)
        self.assertTrue(r["ok"], r)
        pm = r["process_map"]
        self.assertEqual((pm["status"], pm["version"]), ("ok", "mp-v01"))
        self.assertEqual([b["id"] for b in pm["blocks"]], ["MAPN-001", "MAPN-002", "MAPN-003"])
        self.assertEqual(pm["digest"], P["load"](self.eng)["digest"])
        self.assertIn("validation", {b["kind"] for b in pm["blockers"]})
        self.assertEqual(r["next_action"]["action"], "/capture",
                         "mapa por validar e nada mais em curso: rever com o dono")

    def test_a_map_that_moves_under_the_read_is_never_summarised(self):
        self.published()
        boot = {"snapshot": {"inputs": {"_map/map.json": "0" * 64}}}
        pm = W["_process_map_context"](self.eng, boot, 40)
        self.assertEqual(pm["status"], "retry")

    def test_over_budget_is_partial_and_the_blockers_all_stay(self):
        self.published()
        s = P["summary"](self.eng, "resume", budget=1)
        self.assertTrue(s["partial"])
        self.assertEqual(s["omitted"], ["MAPN-002", "MAPN-003"])
        self.assertIn("--budget 3", s["expand"])
        full = P["summary"](self.eng, "resume")
        self.assertEqual(s["blockers"], full["blockers"])
        zero = W["_process_map_context"](
            self.eng, {"snapshot": {"inputs": {"_map/map.json": P["load"](self.eng)["digest"]}}},
            0)
        self.assertEqual(zero["blocks"], [])
        self.assertTrue(zero["blockers"])

    def test_the_task_asks_for_the_detail_it_needs(self):
        self.published()
        light = P["summary"](self.eng, "resume")
        self.assertFalse([b for b in light["blocks"] if "detail" in b])
        deep = P["summary"](self.eng, "blueprint")
        step = next(b for b in deep["blocks"] if b["id"] == "MAPN-002")
        self.assertEqual(len(step["detail"]), 2)
        self.assertEqual(step["evidence"], ["_capture/process-model.md#PM-001"])

    def test_no_map_is_a_capacity_not_evaluated(self):
        r = W["resume"](self.eng)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["process_map"]["status"], "absent")
        self.assertNotEqual(r["next_action"]["action"], "/capture")

    def test_a_pending_operation_stops_the_resume_before_the_map(self):
        self.published()
        (self.eng / "_ops").mkdir(exist_ok=True)
        (self.eng / "_ops" / "pending.json").write_text("{", encoding="utf-8")
        r = W["resume"](self.eng)
        self.assertFalse(r["ok"])
        self.assertEqual(r["code"], "RECOVERY_REQUIRED")
        self.assertNotIn("process_map", r)


class MAP22_Actualidade(Base):

    def setUp(self):
        super().setUp()
        self.published()
        self.validate()
        self.pm = self.eng / "_capture" / "process-model.md"

    def test_an_editorial_change_is_revalidated_and_keeps_the_validation(self):
        self.pm.write_text(self.pm.read_text(encoding="utf-8") + "\nnota editorial\n",
                           encoding="utf-8")
        fr = P["freshness"](self.eng, P["load"](self.eng)["map"])
        self.assertEqual(fr["changed"], [{"source": "_capture/process-model.md",
                                          "missing": False, "anchors": "unchanged",
                                          "affected": []}])
        self.assertIn("source", {b["kind"] for b in P["summary"](self.eng)["blockers"]})
        nxt = W["resume"](self.eng)["next_action"]
        self.assertTrue(nxt["action"].startswith("process_map.py revalidate"), nxt)
        self.assertIn("--source _capture/process-model.md", nxt["action"])
        d = P["revalidate"](self.eng, ["_capture/process-model.md"],
                            "só uma nota no fim do ficheiro", "analista", date="2026-09-25")
        self.publish_draft(d)
        v = P["validation"](self.eng)
        self.assertEqual((v["status"], v.get("carried_from")), ("validated", "mp-v01"))
        self.assertEqual(P["summary"](self.eng)["freshness"]["state"], "current")

    def test_a_material_change_needs_the_elements_reviewed_and_a_new_validation(self):
        self.pm.write_text(self.pm.read_text(encoding="utf-8").replace(
            "soma o prémio ao spread", "soma o prémio e o frete ao spread"), encoding="utf-8")
        fr = P["freshness"](self.eng, P["load"](self.eng)["map"])
        self.assertEqual(fr["changed"][0]["affected"], ["MAPE-002", "MAPN-002"])
        unreviewed = P["revalidate"](self.eng, ["_capture/process-model.md"], "regra mudou",
                                     "analista", date="2026-09-25")
        self.assertIn(P["MAP_REF_STALE"], {e["code"] for e in
                                            P["check"](self.eng, unreviewed)["errors"]})
        reviewed = P["revalidate"](self.eng, ["_capture/process-model.md"], "regra mudou",
                                   "analista", reviewed=fr["changed"][0]["affected"],
                                   date="2026-09-25")
        self.publish_draft(reviewed)
        self.assertEqual(P["validation"](self.eng)["status"], "stale",
                         "uma mudança material nunca herda a validação")

    def test_a_digest_swapped_without_a_record_never_returns_to_current(self):
        self.pm.write_text(self.pm.read_text(encoding="utf-8") + "\nnota\n", encoding="utf-8")
        d = json.loads((self.eng / "_map" / "map.json").read_text("utf-8"))
        d.pop("version")
        d["base"] = P["load"](self.eng)["digest"]
        for s in d["based_on"]:
            if s["path"] == "_capture/process-model.md":
                s["sha256"] = P["_sha"](self.pm.read_bytes())
        self.publish_draft(d)
        self.assertEqual(P["summary"](self.eng)["freshness"]["state"], "current")
        self.assertEqual(P["validation"](self.eng)["status"], "stale",
                         "sem `revalidations` a validação não se transporta")

    def test_revalidate_refuses_a_source_that_did_not_move(self):
        with self.assertRaises(ValueError):
            P["revalidate"](self.eng, ["enquadramento.md"], "nada", "analista")


class MAP24_Dashboard(Base):

    def test_the_map_tab_reads_the_motor_and_is_stable(self):
        self.published()
        a = D["process_map_state"](self.eng)
        b = D["process_map_state"](self.eng)
        self.assertTrue(a["available"])
        self.assertEqual(a, b)
        self.assertEqual(a["svg"], P["render_svg"](P["load"](self.eng)["map"]))
        self.assertEqual(len(a["blocks"]), 3)

    def test_without_a_map_the_tab_says_so(self):
        self.assertEqual(D["process_map_state"](self.eng), {"available": False})

    def test_the_tab_is_declared_and_the_map_dir_triggers_a_rebuild(self):
        self.assertIn("mapa", [k for k, _, _ in D["TAB_SPEC"]])
        self.assertIn("_map", D["INDEX_DIRS"])
        hook = (ROOT / ".claude" / "hooks" / "on-su-change.py").read_text(encoding="utf-8")
        self.assertIn('"_map/"', hook)


class SUAntiga(Base):

    def test_a_su_without_the_elementos_column_projects_as_unevaluated(self):
        su = self.eng / "shared-understanding.md"
        su.write_text(su.read_text(encoding="utf-8").replace(
            "| id | lens | claim | evidência | verificado_em | validade | ronda |\n|---|---|---|---|---|---|---|\n",
            "| id | lens | claim | evidência | verificado_em | validade | ronda |\n|---|---|---|---|---|---|---|\n"
            "| C-001 | data | facto antigo | fonte | 2026-01-01 | organizacional | R-01 |\n"),
            encoding="utf-8")
        self.published()
        pr = P["project"](self.eng)
        self.assertIn("C-001", pr["unevaluated"])
        self.assertIn("MAPN-002", pr["dark"], "sem associação, o passo fica por investigar")
        self.assertNotIn("MAPN-001", pr["dark"], "um início não precisa de linha própria")
        self.assertEqual(pr["elements"]["MAPN-002"]["rows"], [])


if __name__ == "__main__":
    unittest.main()
