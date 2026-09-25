"""process-map M1 — o motor do mapa: integridade, referências, publicação e recuperação.

Casos (docs/process-map/PLANO.md §15): MAP-03 (ligações), MAP-04 (evidência), MAP-05 (dois
CALC iguais em workbooks diferentes), MAP-06 (transferência), MAP-09 (repetição), MAP-10
(dois autores; queda a meio), MAP-11 (fonte muda entre rascunho e publicação), MAP-12
(linhagem: retirar, dividir, reutilizar), versão futura não suportada, e a primeira
verificação estrutural de MAP-01/02 (o P-0 tem de constar das fontes consumidas). MAP-25
vive em `test_process_map_guard.py`.

O motor carrega-se do kernel (`process_map.py` ao lado dos outros motores); enquanto não
estiver lá, do staging `docs/process-map/M1/staging/kernel/tools/` (a guarda de `library/` impede esta
sessão de o escrever — o mantenedor copia; ver docs/process-map/M1/RELATORIO.md).

    python .claude/tests/test_process_map_core.py
"""
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "library" / "kernel" / "tools" / "process_map.py"
STAGING = ROOT / "docs" / "process-map" / "M1" / "staging" / "kernel" / "tools" / "process_map.py"
MOTOR = LIB if LIB.is_file() else STAGING
P = runpy.run_path(str(MOTOR))
L = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_handoff_legacy.py"), run_name="helpers")
O = L["O"]

PROCESS_MODEL = """# Process Model — eng

## 1. File map

## 3. Business rules (PM-NNN)

| id | rule | state | evidence | verificado_em | validade |
|---|---|---|---|---|---|
| PM-001 | O preço de referência soma o prémio ao spread | Assumed | Calc!B9 | 2026-01-01 | financeiro |

## 4. Process synopsis (cross-source)

- OBSERVED — `Resumo`: o resumo diário é enviado aos comerciais — `notas.docx · ¶3`; `PM-001`.
- INFERRED — o ficheiro é gravado para consulta — `PM-001`.

## 4bis. Cadeia de cálculo (por saída)

CALC-001 copiado do motor.

## 6. Interrogation list (PM-U-NNN)

| id | question | why it matters |
|---|---|---|
| PM-U-001 | Quem consome o resumo ao fim de semana? | muda o consumidor |
"""

ENQUADRAMENTO = """# Enquadramento — eng

## T2 · trigger

Todos os dias úteis, às 08:00.

## T4 · outcomes

O preço de referência chega aos comerciais antes das 10:00.
"""

DECISIONS = """# Decisions

## D-001 — Âmbito de entrega SCOPE-0001

- **Timestamp**: 2026-01-02T09:00:00Z
"""


def calc_chain(label):
    return {"tool": {"name": "xlsx_extract", "pass": "calc-chain"},
            "blocks": [{"id": "CALC-001", "sheet": "Calc", "anchor": "B9", "label": label,
                        "steps": [{"cell": "B9", "formula": "=B2+B3"}]}]}


def engagement(base: Path) -> Path:
    eng = L["novo"](base)
    cap = eng / "_capture"
    cap.mkdir()
    (cap / "process-model.md").write_text(PROCESS_MODEL, encoding="utf-8")
    (cap / "precos.xlsx.calc-chain.json").write_text(json.dumps(calc_chain("preço")),
                                                     encoding="utf-8")
    (cap / "precos-2024.xlsx.calc-chain.json").write_text(json.dumps(calc_chain("preço 2024")),
                                                          encoding="utf-8")
    (eng / "enquadramento.md").write_text(ENQUADRAMENTO, encoding="utf-8")
    (eng / "decisions.md").write_text(DECISIONS, encoding="utf-8")
    return eng


def draft_v1() -> dict:
    """Um mapa mínimo que coloca todas as unidades da fixture."""
    return {
        "schema_version": "process-map/1", "engagement_id": "novo", "perspective": "as_is",
        "lanes": [{"id": "MAPL-001", "label": "Fixador", "kind": "actor"},
                  {"id": "MAPL-002", "label": "Comerciais", "kind": "consumer"}],
        "nodes": [
            {"id": "MAPN-001", "kind": "trigger", "label": "Dia útil", "lane": "MAPL-001",
             "order": 0, "marker": "OBSERVED", "evidence": [{"ref": "enquadramento.md#T2"}]},
            {"id": "MAPN-002", "kind": "step", "label": "Calcula o preço", "lane": "MAPL-001",
             "order": 1, "marker": "OBSERVED",
             "evidence": [{"ref": "_capture/process-model.md#PM-001"}]},
            {"id": "MAPN-003", "kind": "output", "label": "Resumo diário", "lane": "MAPL-002",
             "order": 2, "marker": "OBSERVED",
             "evidence": [{"ref": "_capture/process-model.md#§4:Resumo"}]}],
        "edges": [
            {"id": "MAPE-001", "src": "MAPN-001", "dst": "MAPN-002", "kind": "normal",
             "marker": "OBSERVED", "evidence": [{"ref": "enquadramento.md#T2"}]},
            {"id": "MAPE-002", "src": "MAPN-002", "dst": "MAPN-003", "kind": "normal",
             "marker": "OBSERVED", "evidence": [{"ref": "_capture/process-model.md#PM-001"}]}],
        "details": [
            {"id": "MAPD-001", "attaches_to": ["MAPN-002"], "kind": "calculation",
             "label": "preço", "marker": "OBSERVED",
             "ref": {"ref": "_capture/precos.xlsx.calc-chain.json#CALC-001"}},
            {"id": "MAPD-002", "attaches_to": ["MAPN-002"], "kind": "calculation",
             "label": "preço 2024", "marker": "OBSERVED",
             "ref": {"ref": "_capture/precos-2024.xlsx.calc-chain.json#CALC-001"}}],
        "gaps": [{"id": "MAPG-001", "attaches_to": ["MAPN-003"],
                  "question": "Quem consome o resumo ao fim de semana?",
                  "pm_u_ref": "PM-U-001"}],
        "orphans": [], "retired_ids": []}


def codes(verdict, key="errors"):
    return sorted({d["code"] for d in verdict[key]})


class Base(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.eng = engagement(self.base)
        self.outside = self.base / "drafts"
        self.outside.mkdir()

    def stamped(self, draft=None):
        out, _filled = P["stamp"](self.eng, draft or draft_v1())
        return out

    def save(self, draft, name="draft.json"):
        p = self.outside / name
        p.write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
        return p

    def publish(self, draft):
        return P["publish"](self.eng, draft, self.save(draft))

    def cli(self, *args):
        env = dict(os.environ, AISA_ENGAGEMENTS_ROOT=str(self.base), PYTHONIOENCODING="utf-8")
        return subprocess.run([sys.executable, "-B", str(MOTOR), *args], capture_output=True,
                              text=True, encoding="utf-8", env=env)


class Fundacao(Base):

    def test_a_complete_stamped_draft_is_valid_and_places_every_unit(self):
        v = P["check"](self.eng, self.stamped())
        self.assertTrue(v["valid"], v["errors"])
        self.assertEqual(v["transfer"]["units"], 5)
        self.assertEqual(v["transfer"]["missing"], [])

    def test_stamp_fills_only_what_is_missing(self):
        d = draft_v1()
        d["nodes"][1]["evidence"][0]["sha256"] = "0" * 64
        out, filled = P["stamp"](self.eng, d)
        self.assertEqual(out["nodes"][1]["evidence"][0]["sha256"], "0" * 64,
                         "stamp substituiu um digest existente")
        self.assertIn("base", filled)
        self.assertEqual(sorted(s["path"] for s in out["based_on"]),
                         ["_capture/precos-2024.xlsx.calc-chain.json",
                          "_capture/precos.xlsx.calc-chain.json",
                          "_capture/process-model.md", "enquadramento.md"])
        self.assertIn(P["MAP_REF_STALE"], codes(P["check"](self.eng, out)))


class MAP03_Ligacoes(Base):

    def test_dangling_lane_edge_end_and_attachment_are_refused(self):
        d = self.stamped()
        d["nodes"][0]["lane"] = "MAPL-099"
        d["edges"][0]["dst"] = "MAPN-099"
        d["details"][0]["attaches_to"] = ["MAPE-099"]
        v = P["check"](self.eng, d)
        wheres = sorted(e["where"] for e in v["errors"] if e["code"] == P["MAP_DANGLING"])
        self.assertEqual(wheres, ["details/MAPD-001/attaches_to", "edges/MAPE-001/dst",
                                  "nodes/MAPN-001/lane"])
        r = self.publish(d)
        self.assertFalse(r["published"])
        self.assertFalse((self.eng / "_map").exists(), "uma recusa deixou rasto em _map/")

    def test_a_wrong_prefix_is_a_schema_error(self):
        d = self.stamped()
        d["nodes"][0]["id"] = "MAP-N-001"
        self.assertIn(P["MAP_SCHEMA"], codes(P["check"](self.eng, d)))


class MAP04_Evidencia(Base):

    def test_an_observed_node_without_evidence_is_refused(self):
        d = self.stamped()
        d["nodes"][1]["evidence"] = []
        self.assertIn(P["MAP_NO_EVIDENCE"], codes(P["check"](self.eng, d)))

    def test_a_detail_with_a_valid_ref_needs_no_evidence_field(self):
        d = self.stamped()
        self.assertNotIn("evidence", d["details"][0])
        self.assertTrue(P["check"](self.eng, d)["valid"])

    def test_unknown_needs_an_attached_question_not_an_invented_source(self):
        d = self.stamped()
        d["nodes"][2]["marker"] = "UNKNOWN"
        d["gaps"] = []
        d["orphans"] = [{"ref": "_capture/process-model.md#PM-U-001", "reason": "undetermined",
                         "materiality": "undetermined", "note": "por avaliar"}]
        self.assertIn(P["MAP_UNKNOWN_WITHOUT_GAP"], codes(P["check"](self.eng, d)))
        d["gaps"] = draft_v1()["gaps"]
        v = P["check"](self.eng, d)
        self.assertTrue(v["valid"], v["errors"])
        self.assertIn("MAP-UNKNOWN", codes(v, "gaps"))

    def test_an_unresolvable_reference_is_refused(self):
        d = self.stamped()
        d["nodes"][1]["evidence"].append({"ref": "_capture/process-model.md#PM-999",
                                          "sha256": "0" * 64})
        self.assertIn(P["MAP_REF_UNRESOLVED"], codes(P["check"](self.eng, d)))

    def test_coordinated_state_is_not_evidence(self):
        r = P["resolve_ref"](self.eng, "_map/map.json#MAPN-001")
        self.assertEqual(r["status"], "unresolved")
        r = P["resolve_ref"](self.eng, "../fora.md")
        self.assertEqual(r["status"], "unresolved")


class MAP05_CalcPorFicheiro(Base):

    def test_the_same_calc_id_in_two_workbooks_resolves_separately(self):
        a = P["resolve_ref"](self.eng, "_capture/precos.xlsx.calc-chain.json#CALC-001")
        b = P["resolve_ref"](self.eng, "_capture/precos-2024.xlsx.calc-chain.json#CALC-001")
        self.assertEqual((a["status"], b["status"]), ("ok", "ok"))
        self.assertNotEqual(a["digest"], b["digest"])
        self.assertNotEqual(a["unit"], b["unit"])

    def test_an_unqualified_calc_is_ambiguous(self):
        r = P["resolve_ref"](self.eng, "_capture/process-model.md#CALC-001")
        self.assertEqual(r["status"], "ambiguous")
        d = self.stamped()
        d["details"][1]["ref"] = {"ref": "_capture/process-model.md#CALC-001"}
        self.assertIn(P["MAP_REF_AMBIGUOUS"], codes(P["check"](self.eng, d)))


class MAP06_Transferencia(Base):

    def test_every_unplaced_unit_is_named(self):
        d = self.stamped()
        d["nodes"][2]["evidence"] = [{"ref": "enquadramento.md#T4"}]
        d["details"] = d["details"][:1]
        d["gaps"][0].pop("pm_u_ref")
        d = self.stamped(d)
        v = P["check"](self.eng, d)
        self.assertEqual(v["transfer"]["missing"],
                         ["_capture/precos-2024.xlsx.calc-chain.json#CALC-001",
                          "_capture/process-model.md#PM-U-001",
                          "_capture/process-model.md#§4:Resumo"])
        self.assertIn(P["MAP_TRANSFER_MISSING"], codes(v))

    def test_an_explicit_orphan_places_the_unit_but_stays_open(self):
        d = self.stamped()
        d["details"] = d["details"][:1]
        d["orphans"] = [{"ref": "_capture/precos-2024.xlsx.calc-chain.json#CALC-001",
                         "reason": "gap_in_map", "materiality": "material",
                         "note": "ainda não se sabe em que passo entra"}]
        v = P["check"](self.eng, self.stamped(d))
        self.assertTrue(v["valid"], v["errors"])
        self.assertIn("MAP-ORPHAN-OPEN", codes(v, "gaps"), "um órfão material ficou fechado")

    def test_a_material_exclusion_needs_an_existing_decision(self):
        d = self.stamped()
        d["details"] = d["details"][:1]
        orphan = {"ref": "_capture/precos-2024.xlsx.calc-chain.json#CALC-001",
                  "reason": "out_of_scope", "materiality": "material",
                  "note": "o cálculo de 2024 sai do âmbito"}
        d["orphans"] = [dict(orphan)]
        self.assertIn(P["MAP_ORPHAN_NO_AUTHORITY"], codes(P["check"](self.eng, d)))
        d["orphans"] = [dict(orphan, decision_ref="D-009")]
        self.assertIn(P["MAP_ORPHAN_NO_AUTHORITY"], codes(P["check"](self.eng, d)))
        d["orphans"] = [dict(orphan, decision_ref="D-001")]
        self.assertTrue(P["check"](self.eng, d)["valid"])
        d["orphans"] = [dict(orphan, decision_ref="D-001", note=" ")]
        self.assertIn(P["MAP_ORPHAN_UNJUSTIFIED"], codes(P["check"](self.eng, d)))


class MAP01_P0Consumido(Base):

    def test_the_enquadramento_must_be_among_the_consumed_sources(self):
        d = self.stamped()
        d["based_on"] = [s for s in d["based_on"] if s["path"] != "enquadramento.md"]
        d["nodes"][0]["evidence"] = [{"ref": "_capture/process-model.md#PM-001"}]
        d["edges"][0]["evidence"] = [{"ref": "_capture/process-model.md#PM-001"}]
        v = P["check"](self.eng, self.stamped(d) | {"based_on": d["based_on"]})
        self.assertIn(P["MAP_P0_NOT_CONSUMED"], codes(v))


class MAP09_Repeticao(Base):

    def test_replaying_the_same_draft_creates_no_new_version(self):
        d = self.stamped()
        a = self.publish(d)
        self.assertTrue(a["published"], a)
        self.assertEqual(a["version"], "mp-v01")
        b = self.publish(d)
        self.assertTrue(b["published"])
        self.assertTrue(b["replayed"])
        self.assertEqual(b["version"], "mp-v01")
        self.assertEqual(sorted(p.name for p in (self.eng / "_map" / "history").iterdir()),
                         ["mp-v01.json"])
        self.assertEqual((self.eng / "_map" / "map.json").read_bytes(),
                         (self.eng / "_map" / "history" / "mp-v01.json").read_bytes())
        st = P["load"](self.eng)
        self.assertEqual((st["status"], st["map"]["version"]), ("ok", "mp-v01"))


class MAP10_Concorrencia(Base):

    def test_the_second_author_on_the_same_base_is_refused(self):
        a = self.stamped()
        b = self.stamped()
        b["nodes"][1]["label"] = "Calcula o preço (versão B)"
        self.assertTrue(self.publish(a)["published"])
        r = self.publish(b)
        self.assertFalse(r["published"])
        self.assertIn(P["MAP_BASE_STALE"], codes(r["verdict"]))
        self.assertEqual(P["load"](self.eng)["map"]["nodes"][1]["label"], "Calcula o preço")

    def test_the_coordinator_refuses_a_stale_base_even_past_the_check(self):
        a = self.stamped()
        self.assertTrue(self.publish(a)["published"])
        b = self.stamped(dict(draft_v1(), base=""))
        b["nodes"][1]["label"] = "outra"
        orig = P["check"]
        try:
            P["publish"].__globals__["check"] = lambda *a, **k: {"valid": True}
            r = self.publish(b)
        finally:
            P["publish"].__globals__["check"] = orig
        self.assertFalse(r["published"])
        self.assertEqual((r["code"], r["source_code"]), ("STALE_INPUT", "BASE_CHANGED"))

    CRASH = textwrap.dedent("""
        import json, os, runpy, sys
        P = runpy.run_path(r"{motor}")
        O = P["_mod"]("operation")
        def sabotado(e, intent):
            done = []
            for rel in sorted(intent["after"]):
                src = os.path.join(e, intent["staging"], rel.replace("/", "__"))
                dst = os.path.join(e, rel)
                os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
                O["_atomic_write"](dst, open(src, encoding="utf-8").read())
                done.append(rel)
                os._exit(9)
            return done
        O["run"].__globals__["_publish"] = sabotado
        d = json.load(open(r"{draft}", encoding="utf-8"))
        P["publish"](r"{eng}", d)
    """)

    def test_a_crash_mid_publish_leaves_a_visible_pending_and_recovers_whole(self):
        d = self.stamped()
        path = self.save(d)
        p = subprocess.run([sys.executable, "-c", self.CRASH.format(motor=MOTOR, draft=path,
                                                                    eng=self.eng)],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 9, p.stderr)
        self.assertEqual(O["status"](self.eng)["state"], O["PENDING_OPERATION"])
        r = self.publish(d)
        self.assertFalse(r["published"])
        self.assertEqual(r["code"], "RECOVERY_REQUIRED")
        O["recover"](self.eng)
        again = self.publish(d)
        self.assertTrue(again["published"], again)
        self.assertTrue(again["replayed"], "a recuperação não completou a operação original")
        self.assertEqual((self.eng / "_map" / "map.json").read_bytes(),
                         (self.eng / "_map" / "history" / "mp-v01.json").read_bytes())


class MAP11_FonteMuda(Base):

    def test_a_source_changed_after_stamping_refuses_and_keeps_the_draft(self):
        d = self.stamped()
        path = self.save(d)
        pm = self.eng / "_capture" / "process-model.md"
        pm.write_text(pm.read_text(encoding="utf-8") + "\nnota nova\n", encoding="utf-8")
        before = path.read_bytes()
        r = P["publish"](self.eng, d, path)
        self.assertFalse(r["published"])
        self.assertIn(P["MAP_SOURCE_STALE"], codes(r["verdict"]))
        self.assertEqual(path.read_bytes(), before, "o rascunho foi alterado")
        self.assertFalse((self.eng / "_map").exists())

    def test_the_coordinator_refuses_a_source_that_moves_past_the_check(self):
        d = self.stamped()
        (self.eng / "enquadramento.md").write_text(ENQUADRAMENTO + "\nmudou\n",
                                                   encoding="utf-8")
        orig = P["check"]
        try:
            P["publish"].__globals__["check"] = lambda *a, **k: {"valid": True}
            r = self.publish(d)
        finally:
            P["publish"].__globals__["check"] = orig
        self.assertFalse(r["published"])
        self.assertEqual((r["code"], r["source_code"]), ("STALE_INPUT", "STALE_INPUT"))


class MAP12_Linhagem(Base):

    def setUp(self):
        super().setUp()
        self.assertTrue(self.publish(self.stamped())["published"])
        self.base_digest = P["load"](self.eng)["digest"]

    def v2(self):
        d = draft_v1()
        d["base"] = self.base_digest
        return d

    def test_an_element_cannot_vanish_without_being_retired(self):
        d = self.v2()
        d["edges"] = d["edges"][:1]
        self.assertIn(P["MAP_ID_DROPPED"], codes(P["check"](self.eng, self.stamped(d))))

    def test_a_split_keeps_the_old_identity_and_names_its_successors(self):
        d = self.v2()
        step = d["nodes"][1]
        d["nodes"][1] = dict(step, id="MAPN-004", label="Recolhe cotações", was=["MAPN-002"])
        d["nodes"].append(dict(step, id="MAPN-005", label="Aplica margem", order=2,
                               was=["MAPN-002"]))
        d["retired_ids"] = [{"id": "MAPN-002", "reason": "dividido em MAPN-004 e MAPN-005"}]
        for e in d["edges"]:
            e["src"] = "MAPN-005" if e["src"] == "MAPN-002" else e["src"]
            e["dst"] = "MAPN-004" if e["dst"] == "MAPN-002" else e["dst"]
        d["details"][0]["attaches_to"] = ["MAPN-004"]
        d["details"][1]["attaches_to"] = ["MAPN-005"]
        r = self.publish(self.stamped(d))
        self.assertTrue(r["published"], r.get("verdict"))
        self.assertEqual(r["version"], "mp-v02")
        v1 = json.loads((self.eng / "_map" / "history" / "mp-v01.json").read_text("utf-8"))
        self.assertIn("MAPN-002", {n["id"] for n in v1["nodes"]}, "a história foi reescrita")

    def test_a_retired_id_is_never_reused(self):
        d = self.v2()
        d["edges"] = d["edges"][:1]
        d["retired_ids"] = [{"id": "MAPE-002", "reason": "ligação redundante"}]
        self.assertTrue(self.publish(self.stamped(d))["published"])
        d3 = draft_v1()
        d3["base"] = P["load"](self.eng)["digest"]
        v = P["check"](self.eng, self.stamped(d3))
        self.assertIn(P["MAP_ID_REUSED"], codes(v))

    def test_was_must_point_to_something_that_existed(self):
        d = self.v2()
        d["nodes"][2]["was"] = ["MAPN-077"]
        self.assertIn(P["MAP_WAS_UNKNOWN"], codes(P["check"](self.eng, self.stamped(d))))


class VersaoFutura(Base):

    def test_a_future_schema_is_read_as_unsupported_and_never_overwritten(self):
        (self.eng / "_map").mkdir()
        (self.eng / "_map" / "map.json").write_text(
            json.dumps({"schema_version": "process-map/2"}), encoding="utf-8")
        self.assertEqual(P["load"](self.eng)["status"], "unsupported")
        d = self.stamped()
        r = self.publish(d)
        self.assertFalse(r["published"])
        self.assertIn(P["MAP_PUBLISHED_INVALID"], codes(r["verdict"]))
        self.assertEqual(json.loads((self.eng / "_map" / "map.json").read_text("utf-8")),
                         {"schema_version": "process-map/2"})


class CLI(Base):

    def test_exit_codes_separate_valid_gaps_and_errors(self):
        d = self.stamped()
        d["gaps"] = []
        d["orphans"] = [{"ref": "_capture/process-model.md#PM-U-001", "reason": "undetermined",
                         "materiality": "undetermined", "note": "por avaliar"}]
        path = self.save(d)
        r = self.cli("check", "--engagement", "novo", "--draft", str(path), "--json")
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        d["orphans"] = []
        path = self.save(d)
        r = self.cli("check", "--engagement", "novo", "--draft", str(path), "--json")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn(P["MAP_TRANSFER_MISSING"], r.stdout)

    def test_a_draft_inside_the_engagement_is_refused(self):
        inside = self.eng / "rascunho.json"
        inside.write_text(json.dumps(self.stamped()), encoding="utf-8")
        r = self.cli("stamp", "--engagement", "novo", "--draft", str(inside))
        self.assertEqual(r.returncode, 2)
        r = self.cli("publish", "--engagement", "novo", "--draft", str(inside))
        self.assertEqual(r.returncode, 2)
        self.assertFalse((self.eng / "_map").exists())

    def test_publish_and_status_through_the_cli(self):
        path = self.save(self.stamped())
        r = self.cli("publish", "--engagement", "novo", "--draft", str(path), "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = self.cli("status", "--engagement", "novo", "--json")
        self.assertEqual(json.loads(r.stdout)["version"], "mp-v01")


if __name__ == "__main__":
    unittest.main()
