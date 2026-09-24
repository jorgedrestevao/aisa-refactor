# -*- coding: utf-8 -*-
"""handoff-v1 F8.1 — as ferramentas dos pilotos (`docs/handoff-v1/F8/tools/f8.py`).

Desenho: `docs/handoff-v1/F8/DESENHO.md` §1, §3, §5. O instrumento não é de confiar por
decreto: cada verificação que o F8 usa para dizer «a retoma preservou», «o executor não leu
o `expected`» ou «a evidência do avaliador existe» tem aqui o caso que a faz falhar.

    python .claude/tests/test_f8_tools.py
"""
import hashlib
import json
import re
import runpy
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
F = runpy.run_path(str(ROOT / "docs" / "handoff-v1" / "F8" / "tools" / "f8.py"))
E2E = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_hv1_02_discovery.py"))
F8Error = F["F8Error"]


def arvore(base):
    return {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(base).rglob("*")) if p.is_file()
            and "__pycache__" not in p.parts}


def eng_com_analise(tmp):
    eng = E2E["engagement"](Path(tmp))
    E2E["publish_analysis"](eng)
    return eng


class RunLog(unittest.TestCase):

    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_events_are_appended_in_order_with_a_sequence(self):
        F["runlog_add"](self.d, "R3", "segment_start", {"goal": "S1"}, "S1")
        F["runlog_add"](self.d, "R3", "usage", {"role": "executor", "tokens": 10}, "S1")
        evs = F["runlog_read"](self.d, "R3")
        self.assertEqual([e["seq"] for e in evs], [1, 2])
        self.assertEqual(evs[1]["data"]["tokens"], 10)

    def test_an_unknown_event_type_or_run_id_is_refused(self):
        with self.assertRaises(F8Error):
            F["runlog_add"](self.d, "R3", "achei_bem", {})
        with self.assertRaises(F8Error):
            F["runlog_add"](self.d, "fx02", "note", {})
        with self.assertRaises(F8Error):
            F["runlog_add"](self.d, "R3", "usage", {"role": "orquestrador"})

    def test_an_unreadable_line_is_an_error_never_skipped(self):
        F["runlog_add"](self.d, "R1", "note", {"x": 1})
        with open(self.d / "R1" / "run-log.jsonl", "a", encoding="utf-8") as fh:
            fh.write("{partido\n")
        with self.assertRaises(F8Error) as cm:
            F["runlog_read"](self.d, "R1")
        self.assertEqual(cm.exception.code, "RUNLOG_UNREADABLE")


class Snapshots(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.eng = self.tmp / "projects" / "f8-r9-fx"
        (self.eng / "_graph").mkdir(parents=True)
        (self.eng / "shared-understanding.md").write_text("# SU\n| U-001 |\n", encoding="utf-8")
        (self.eng / "_graph" / "nodes.json").write_text("{}\n", encoding="utf-8")
        self.exec = self.tmp / "execucoes"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_snapshot_copies_everything_and_is_immutable(self):
        out = F["snapshot_save"](self.eng, self.exec, "R9", "S1-fim")
        self.assertEqual(out["files"], 2)
        self.assertEqual(F["snapshot_verify"](self.exec, "R9", "S1-fim"), [])
        with self.assertRaises(F8Error) as cm:
            F["snapshot_save"](self.eng, self.exec, "R9", "S1-fim")
        self.assertEqual(cm.exception.code, "SNAPSHOT_EXISTS")

    def test_a_changed_snapshot_is_reported(self):
        F["snapshot_save"](self.eng, self.exec, "R9", "S1-fim")
        alvo = self.exec / "R9" / "snapshots" / "S1-fim" / "engagement" / \
            "shared-understanding.md"
        alvo.write_text("# SU mexida\n", encoding="utf-8")
        codes = [a["code"] for a in F["snapshot_verify"](self.exec, "R9", "S1-fim")]
        self.assertEqual(codes, ["CHANGED"])

    def test_restore_never_writes_over_an_engagement(self):
        F["snapshot_save"](self.eng, self.exec, "R9", "S1-fim")
        with self.assertRaises(F8Error) as cm:
            F["snapshot_restore"](self.exec, "R9", "S1-fim", self.eng)
        self.assertEqual(cm.exception.code, "RESTORE_TARGET_EXISTS")
        novo = self.tmp / "projects" / "f8-r9-fx-reposto"
        F["snapshot_restore"](self.exec, "R9", "S1-fim", novo)
        self.assertEqual(arvore(novo), arvore(self.eng))

    def test_restore_refuses_a_snapshot_that_no_longer_matches_its_manifest(self):
        F["snapshot_save"](self.eng, self.exec, "R9", "S1-fim")
        (self.exec / "R9" / "snapshots" / "S1-fim" / "engagement" / "a-mais.md").write_text(
            "x", encoding="utf-8")
        with self.assertRaises(F8Error) as cm:
            F["snapshot_restore"](self.exec, "R9", "S1-fim", self.tmp / "projects" / "novo")
        self.assertEqual(cm.exception.code, "SNAPSHOT_INVALID")


class Retoma(unittest.TestCase):
    """A verdade congelada contra a declaração do executor novo."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.eng = eng_com_analise(cls.tmp)
        cls.antes = arvore(cls.eng)
        cls.t = F["truth"](cls.eng)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def perfeita(self):
        return {"engagement": self.t["engagement"], "phase": self.t["phase"],
                "route": self.t["route"], "decisions": list(self.t["decisions"]),
                "open_questions": list(self.t["material_open"]),
                "next_step": "/status"}

    def test_the_truth_reads_the_material_questions_and_writes_nothing(self):
        self.assertTrue(self.t["ready"])
        self.assertIn("U-001", self.t["material_open"])
        self.assertIn("U-002", self.t["material_open"])
        self.assertEqual(arvore(self.eng), self.antes)

    def test_a_faithful_declaration_passes(self):
        out = F["check_resume"](self.t, self.perfeita())
        self.assertEqual(out["verdict"], "pass", out["findings"])

    def test_losing_a_material_question_fails(self):
        r = self.perfeita()
        r["open_questions"].remove("U-001")
        out = F["check_resume"](self.t, r)
        self.assertEqual(out["verdict"], "fail")
        self.assertIn(("LOST_QUESTION", "U-001"),
                      [(a["code"], a["detail"]) for a in out["findings"]])

    def test_inventing_a_question_or_a_decision_fails(self):
        r = self.perfeita()
        r["open_questions"].append("U-999")
        r["decisions"].append("D-042")
        codes = {a["code"] for a in F["check_resume"](self.t, r)["findings"]}
        self.assertTrue({"INVENTED_QUESTION", "INVENTED_DECISION"} <= codes)

    def test_a_resolved_row_declared_open_only_warns(self):
        t = json.loads(json.dumps(self.t))
        t["open_ids"] = [i for i in t["open_ids"] if i != "U-003"]
        r = self.perfeita()
        r["open_questions"].append("U-003")
        out = F["check_resume"](t, r)
        self.assertEqual(out["verdict"], "pass")
        self.assertIn("STALE_QUESTION", [a["code"] for a in out["findings"]])

    def test_wrong_phase_route_or_engagement_fails(self):
        for campo, code in (("phase", "PHASE_MISMATCH"), ("route", "ROUTE_MISMATCH"),
                            ("engagement", "WRONG_ENGAGEMENT")):
            r = self.perfeita()
            r[campo] = "outro-" + str(r[campo])
            codes = [a["code"] for a in F["check_resume"](self.t, r)["findings"]]
            self.assertIn(code, codes, campo)

    def test_a_declaration_missing_a_field_is_incomplete(self):
        r = self.perfeita()
        del r["decisions"]
        out = F["check_resume"](self.t, r)
        self.assertEqual(out["verdict"], "fail")
        self.assertIn("REPORT_INCOMPLETE", [a["code"] for a in out["findings"]])

    def test_a_pending_recovery_must_be_named(self):
        t = json.loads(json.dumps(self.t))
        t["resume"]["code"] = "RECOVERY_REQUIRED"
        codes = [a["code"] for a in F["check_resume"](t, self.perfeita())["findings"]]
        self.assertIn("RECOVERY_IGNORED", codes)
        r = self.perfeita()
        r["recovery_required"] = True
        codes = [a["code"] for a in F["check_resume"](t, r)["findings"]]
        self.assertNotIn("RECOVERY_IGNORED", codes)


class Canario(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.eng = self.tmp / "eng"
        (self.eng / "inputs").mkdir(parents=True)
        self.fontes = self.tmp / "fontes"
        self.fontes.mkdir()
        (self.fontes / "pedido.md").write_text(
            "O colaborador pede por email e a chefia responde aprovado sem registo nenhum.",
            encoding="utf-8")
        self.expected = ["A chefia responde aprovado sem registo nenhum e o pedido fica "
                         "perdido na caixa de correio do departamento de compras."]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_text_only_the_expected_has_is_caught(self):
        (self.eng / "shared-understanding.md").write_text(
            "| U-001 | o pedido fica perdido na caixa de correio do departamento |",
            encoding="utf-8")
        out = F["canary"](self.eng, self.expected, [self.fontes])
        self.assertEqual(out["verdict"], "contaminated")

    def test_text_the_sources_also_have_is_not_a_canary(self):
        (self.eng / "shared-understanding.md").write_text(
            "| C-001 | a chefia responde aprovado sem registo nenhum |", encoding="utf-8")
        self.assertEqual(F["canary"](self.eng, self.expected, [self.fontes])["verdict"],
                         "clean")

    def test_copies_of_the_sources_inside_the_engagement_are_ignored(self):
        (self.eng / "inputs" / "copia.md").write_text(self.expected[0], encoding="utf-8")
        self.assertEqual(F["canary"](self.eng, self.expected, [self.fontes])["verdict"],
                         "clean")

    def test_the_real_fixture_has_distinctive_expected_text(self):
        cen = json.loads((ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1" /
                          "fx-hv1-02-pp-constrained" / "scenario.json").read_text(
                              encoding="utf-8"))
        vazio = self.tmp / "vazio"
        vazio.mkdir()
        out = F["canary"](vazio, F["expected_texts"](cen), [
            ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1" /
            "fx-hv1-02-pp-constrained" / "sources"])
        self.assertGreater(out["distinctive_grams"], 20)
        self.assertEqual(out["verdict"], "clean")


class Avaliacao(unittest.TestCase):

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        (self.base / "shared-understanding.md").write_text(
            "| U-001 | arredondamento |\n| C-004 | chefia nunca aprova o seu |\n",
            encoding="utf-8")
        (self.base / "decisions.md").write_text("## D-004 — FC autorizados\n",
                                                encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def tabela(self, **troca):
        itens = [{"id": "E01", "verdict": "cumprido",
                  "locators": ["shared-understanding.md#U-001"], "rationale": "linha U-001"},
                 {"id": "E02", "verdict": "ausente", "locators": [], "rationale": "não há"},
                 {"id": "E03", "verdict": "cumprido", "locators": ["decisions.md:1"],
                  "rationale": "D-004"}]
        for i in itens:
            i.update(troca.get(i["id"], {}))
        return {"run": "R9", "items": itens}

    def test_a_table_whose_evidence_resolves_passes(self):
        out = F["verify_eval"](self.base, self.tabela(), ["E01", "E02", "E03"])
        self.assertEqual(out["verdict"], "pass", out["findings"])
        self.assertEqual(out["counts"]["cumprido"], 2)

    def test_a_locator_that_does_not_resolve_fails(self):
        for loc in ("shared-understanding.md#U-999", "nada.md", "decisions.md:40",
                    "shared-understanding.md#U-00"):
            out = F["verify_eval"](self.base, self.tabela(E01={"locators": [loc]}),
                                   ["E01", "E02", "E03"])
            self.assertIn("LOCATOR_UNRESOLVED", [a["code"] for a in out["findings"]], loc)

    def test_a_verdict_without_evidence_or_an_item_left_out_fails(self):
        out = F["verify_eval"](self.base, self.tabela(E01={"locators": []}),
                               ["E01", "E02", "E03", "E04"])
        codes = [a["code"] for a in out["findings"]]
        self.assertIn("NO_EVIDENCE", codes)
        self.assertIn("MISSING_ITEM", codes)

    def test_an_invalid_verdict_fails(self):
        out = F["verify_eval"](self.base, self.tabela(E02={"verdict": "parcial"}),
                               ["E01", "E02", "E03"])
        self.assertIn("BAD_VERDICT", [a["code"] for a in out["findings"]])


F8 = ROOT / "docs" / "handoff-v1" / "F8"
FIXT = ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1"


def ancoras_citadas(fonte):
    """`pedido.md#P1, #P3; nota-dados.md#D3` → [(ficheiro, âncora), …]; intervalos
    `M1-M5` contam pelas duas pontas."""
    fora = []
    for seg in str(fonte).split(";"):
        m = re.search(r"([\w.-]+\.md)#", seg)
        if not m:
            continue
        for a, b in re.findall(r"#([A-Z]\d+)(?:-([A-Z]\d+))?", seg):
            fora.append((m.group(1), a))
            if b:
                fora.append((m.group(1), b))
    return fora


class MateriaisDosPilotos(unittest.TestCase):
    """Os cartões, as fichas e as mudanças são a referência escrita antes de correr: o que
    citam tem de existir, e nada neles pode ter vindo do `expected`."""

    def setUp(self):
        self.cartoes = sorted((F8 / "cartoes").glob("R*.json"))

    def test_there_is_a_card_and_every_path_it_names_exists(self):
        self.assertTrue(self.cartoes)
        for c in self.cartoes:
            d = json.loads(c.read_text(encoding="utf-8"))
            caminhos = [d["ficha"]] + d["entrega_inicial"] + d["referencia"]
            for s in d["segmentos"]:
                caminhos += list((s.get("mudanca") or {}).values())
            for p in caminhos:
                self.assertTrue((ROOT / p).is_file(), "{}: {}".format(c.name, p))
            self.assertTrue(re.fullmatch(r"f8-r\d+-fx\d+", d["slug"]), d["slug"])
            ids = [s["id"] for s in d["segmentos"]]
            self.assertEqual(len(ids), len(set(ids)))

    def test_every_answer_in_a_client_card_cites_a_source_that_exists(self):
        for ficha in sorted((F8 / "fichas").glob("*.cliente.json")):
            d = json.loads(ficha.read_text(encoding="utf-8"))
            fontes = {p.name: p.read_text(encoding="utf-8")
                      for p in (FIXT / d["fixture"] / "sources").glob("*.md")}
            fontes.update({p.name: p.read_text(encoding="utf-8")
                           for p in (FIXT / "fx-hv1-03-change-impact" / "sources").glob("*.md")})
            for r in d["respostas"]:
                self.assertTrue(r.get("fonte"), r["id"])
                for fich, anc in ancoras_citadas(r["fonte"]):
                    self.assertIn(fich, fontes, "{}: {}".format(r["id"], fich))
                    self.assertIn("[{}]".format(anc), fontes[fich],
                                  "{}: {}#{}".format(r["id"], fich, anc))

    def test_a_change_cites_anchors_that_exist_and_its_ids_do_not_collide(self):
        for exp in sorted((F8 / "mudancas").glob("*/expected.json")):
            d = json.loads(exp.read_text(encoding="utf-8"))
            cen = json.loads((FIXT / d["fixture"] / "scenario.json").read_text(
                encoding="utf-8"))
            e_ids = {e["id"] for e in cen["expected"]}
            fontes = {p.name: p.read_text(encoding="utf-8") for p in exp.parent.glob("*.md")}
            fontes.update({p.name: p.read_text(encoding="utf-8")
                           for p in (FIXT / d["fixture"] / "sources").glob("*.md")})
            ids = [e["id"] for e in d["expected"]]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertEqual(set(ids) & e_ids, set(), exp)
            for e in d["expected"]:
                self.assertTrue(e["must_not"], e["id"])
                for ref in e["source_refs"]:
                    fich, anc = ref.split("#")
                    self.assertIn("[{}]".format(anc), fontes[fich], ref)


class Agregado(unittest.TestCase):

    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_no_executions_is_never_green(self):
        self.assertEqual(F["summary"](self.d)["verdict"], "SEM EXECUÇÃO")
        self.assertEqual(F["summary"](self.d / "nao-existe")["verdict"], "SEM EXECUÇÃO")

    def test_a_failed_resume_or_an_unanswered_question_is_not_met(self):
        F["runlog_add"](self.d, "R3", "usage", {"role": "executor", "tokens": 100,
                                                "tool_uses": 3, "duration_ms": 1000})
        F["runlog_add"](self.d, "R3", "resume_check", {"verdict": "pass"})
        F["runlog_add"](self.d, "R3", "resume_check", {"verdict": "fail"})
        F["runlog_add"](self.d, "R3", "recipient", {"reading": 1, "essential_unanswered": 2})
        F["runlog_add"](self.d, "R3", "evaluation", {"counts": {"cumprido": 5, "violado": 0,
                                                                "ausente": 1}})
        s = F["summary"](self.d)
        self.assertFalse(s["criteria"]["resumes_preserved"]["met"])
        self.assertFalse(s["criteria"]["recipient_essential_unanswered"]["met"])
        self.assertFalse(s["criteria"]["material_items_absent"]["met"])
        self.assertTrue(s["criteria"]["must_not_violations"]["met"])
        self.assertEqual(s["runs"]["R3"]["usage"]["executor"]["tokens"], 100)
        self.assertNotIn("GO", s["verdict"].split())


if __name__ == "__main__":
    unittest.main(verbosity=1)
