"""Frente E (P-15) — a round in progress is not a completed round.

The contract lives in `library/kernel/phases.md` (*Rounds — in progress vs completed*);
`aisa-round` step 3/7 writes `round_in_progress`, and `dashboard.py` reads it.

handoff-v1 F3.3 (decision Q2): the passagem closes by its `lens` coverage record, and the
lens-order guard (`pre-lens-order-check.py`) with its `round_lenses` record is retired.
The guard's cases here (P-R6, engagement resolution, single mode authorised by state)
were eliminated with it: there is no order left to police — the six perspectives are one
analysis. What stays: the open-round rule of the motor, the header reading of the
historical version, and the written contract. New: a profile engagement reads the
perspectives of the open passagem from the `lens` record.

    python .claude/tests/test_round_in_progress.py
"""

import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "library" / "kernel" / "tools" / "dashboard.py"
ROUND_SKILL = ROOT / ".claude" / "skills" / "aisa-round" / "SKILL.md"
START_SKILL = ROOT / ".claude" / "skills" / "aisa-start" / "SKILL.md"
PHASES = ROOT / "library" / "kernel" / "phases.md"
HOOKS = ROOT / ".claude" / "hooks"
SIX = ["business", "operations", "user", "data", "governance", "financial"]


def make_engagement(base, slug, *, round_done="R-00", in_progress="",
                    lens_outputs=None, phase="discovery", round_lenses=None):
    eng = Path(base) / slug
    (eng / "lens-outputs").mkdir(parents=True, exist_ok=True)
    state = {"engagement": slug, "phase": phase, "round": round_done}
    if in_progress:
        state["round_in_progress"] = in_progress
    if round_lenses is not None:
        state["round_lenses"] = round_lenses
    (eng / "_state.json").write_text(json.dumps(state), encoding="utf-8")
    (eng / "shared-understanding.md").write_text("# SU\n", encoding="utf-8")
    for lens, stamped in (lens_outputs or {}).items():
        (eng / "lens-outputs" / f"{lens}.md").write_text(
            f"## {stamped} - {lens}\nFindings.\n", encoding="utf-8")
    return eng


class OutputIsAHeaderNotASubstring(unittest.TestCase):
    """F4: "wrote for R-02" means a `## R-02 …` heading, never a body mention (the
    historical version's reading)."""

    def test_legacy_header_shapes_count(self):
        dash = runpy.run_path(str(DASHBOARD))
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "x.md"
            for header in ("## R-02 — business", "## R-02 (2026-05-29)", "## R-02 — 2026-05-28"):
                f.write_text(header + "\n", encoding="utf-8")
                self.assertTrue(dash["lens_wrote_round"](f, "R-02"), header)
            f.write_text("## R-020 — business\n", encoding="utf-8")
            self.assertFalse(dash["lens_wrote_round"](f, "R-02"), "R-020 is not R-02")


class MotorNamesTheMissingLenses(unittest.TestCase):
    """F5: which lenses stamped the open passagem is a fact the motor publishes."""

    def setUp(self):
        self.dash = runpy.run_path(str(DASHBOARD))

    def test_out_of_order_subset(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = make_engagement(tmp, "eng", round_done="R-00", in_progress="R-01",
                                  lens_outputs={"financial": "R-01", "data": "R-01"})
            got = self.dash["lenses_for_round"](eng, "R-01")
        self.assertEqual(got["corridas"], ["data", "financial"])
        self.assertEqual(got["em_falta"], ["business", "operations", "user", "governance"])

    def test_all_six_means_nothing_missing(self):
        lenses = ["business", "operations", "user", "data", "governance", "financial"]
        with tempfile.TemporaryDirectory() as tmp:
            eng = make_engagement(tmp, "eng", round_done="R-00", in_progress="R-01",
                                  lens_outputs={l: "R-01" for l in lenses})
            got = self.dash["lenses_for_round"](eng, "R-01")
        self.assertEqual(got["em_falta"], [])

    def test_no_open_round_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = make_engagement(tmp, "eng", round_done="R-01")
            self.assertEqual(self.dash["lenses_for_round"](eng, ""),
                             {"ronda": "", "corridas": [], "em_falta": []})

    def test_model_publishes_the_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = make_engagement(tmp, "eng", round_done="R-00", in_progress="R-01",
                                  lens_outputs={"user": "R-01"})
            (eng / "context.json").write_text("{}", encoding="utf-8")
            from datetime import date
            model = self.dash["build_model"](eng, date(2026, 9, 9))
        self.assertEqual(model["engagement"]["lentes_ronda_aberta"]["corridas"], ["user"])


class MotorReadsTheOpenRound(unittest.TestCase):
    """dashboard.py publishes it, with the same staleness rule as the guard."""

    def setUp(self):
        self.dash = runpy.run_path(str(DASHBOARD))

    def test_open_round_published(self):
        self.assertEqual(
            self.dash["_open_round"]({"round": "R-01", "round_in_progress": "R-02"}),
            "R-02")

    def test_stale_and_absent_are_both_empty(self):
        for state in ({"round": "R-02", "round_in_progress": "R-01"},
                      {"round": "R-02", "round_in_progress": "R-02"},
                      {"round": "R-02"},
                      {"round": "R-02", "round_in_progress": ""}):
            self.assertEqual(self.dash["_open_round"](state), "", state)


class ContractIsWritten(unittest.TestCase):
    """The rule lives in the kernel and the skills that write the state."""

    def test_phases_declares_the_two_fields(self):
        text = PHASES.read_text(encoding="utf-8")
        self.assertIn("round_in_progress", text)
        self.assertIn("A round in progress is not a completed round.", text)

    def test_start_seeds_the_field(self):
        self.assertIn('"round_in_progress": ""',
                      START_SKILL.read_text(encoding="utf-8"))

    def test_round_opens_closes_and_offers_close(self):
        text = ROUND_SKILL.read_text(encoding="utf-8")
        self.assertIn("--close", text)
        self.assertIn("round_in_progress", text)
        self.assertIn("`round_in_progress` = `\"\"`", text)

    def test_round_closes_by_the_coverage_record(self):
        text = ROUND_SKILL.read_text(encoding="utf-8")
        self.assertIn("coverage.py round-state", text)
        self.assertIn("coverage.py lens-draft", text)
        self.assertIn("coverage.py finalize", text)
        self.assertIn("lentes_ronda_aberta", text)
        self.assertIn("Passagem guard", text)
        self.assertIn("*Never* close on a count of files", text)
        self.assertNotIn("last of the order** (`financial`)", text)

    def test_the_reviewer_runs_once_at_close_with_fresh_context(self):
        text = ROUND_SKILL.read_text(encoding="utf-8")
        self.assertIn("subagent_type: lens-coverage-reviewer", text)
        self.assertIn("only when the passagem is to close", text)
        self.assertIn("never after `/round <perspective>`", text)
        agent = (ROOT / ".claude" / "agents" / "lens-coverage-reviewer.md").read_text(
            encoding="utf-8")
        self.assertIn("tools: [Read, Grep, Glob]", agent)
        self.assertIn('"name": "lens-coverage-reviewer"', agent)

    def test_the_order_guard_and_its_record_are_retired(self):
        self.assertFalse((HOOKS / "pre-lens-order-check.py").exists())
        settings = (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
        self.assertNotIn("pre-lens-order-check", settings)
        self.assertNotIn("pre-lens-order-check", (HOOKS / "HOOKS.md").read_text(
            encoding="utf-8"))
        phases = PHASES.read_text(encoding="utf-8")
        self.assertNotIn("`_state.json.round_lenses` =", phases)
        self.assertIn("`round_lenses` record are retired", phases)
        text = ROUND_SKILL.read_text(encoding="utf-8")
        self.assertNotIn("`round_lenses` = `{", text)
        self.assertNotIn("round mode: <full|single>", text)


class RecordIsTheSourceForAProfile(unittest.TestCase):
    """handoff-v1 F3.3: a profile engagement reads the open passagem from the `lens`
    coverage record — the six or nothing, plus whether it closes and was reviewed."""

    @classmethod
    def setUpClass(cls):
        cls.dash = runpy.run_path(str(DASHBOARD))
        cls.fix = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_migration.py"))
        cls.mig = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "migrate.py"))
        cls.cov = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "coverage.py"))

    def engagement(self, tmp):
        projects = Path(tmp) / "projects"
        projects.mkdir()
        eng = Path(self.fix["make"](str(projects), self.fix["NOVO"]))
        self.mig["apply"](eng)
        return eng

    def record(self, eng, tmp, round_id, review=None):
        sk = self.cov["lens_skeleton"](eng, round_id)
        sk["generated_at"] = "2026-09-23T20:00:00Z"
        for d in SIX:
            sk["lens_coverage"]["dimensions"][d] = {
                "status": "assessed", "refs": ["C-001"], "justification": "base"}
        sk["lens_coverage"]["conflict_scan"] = {"refs": [], "note": "nenhum conflito"}
        if review:
            sk["semantic_review"] = review
        p = Path(tmp) / "draft-{}.json".format(round_id)
        p.write_text(json.dumps(sk), encoding="utf-8")
        out = self.cov["finalize"](eng, p)
        self.assertTrue(out["published"], out)

    def test_no_record_means_nothing_covered_and_says_why(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.engagement(tmp)
            state = json.loads((eng / "_state.json").read_text(encoding="utf-8"))
            self.assertTrue(state.get("workflow"))
            got = self.dash["lenses_for_round"](eng, "R-01", state)
        self.assertEqual(got["corridas"], [])
        self.assertEqual(got["em_falta"], SIX)
        self.assertEqual(got["fonte"], "registo lens")
        self.assertFalse(got["fecha"])
        self.assertTrue(got["motivos"])

    def test_headers_do_not_count_for_a_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.engagement(tmp)
            (eng / "lens-outputs").mkdir(exist_ok=True)
            for l in SIX:
                (eng / "lens-outputs" / (l + ".md")).write_text(
                    "## R-01 — {}\nx\n".format(l), encoding="utf-8")
            state = json.loads((eng / "_state.json").read_text(encoding="utf-8"))
            got = self.dash["lenses_for_round"](eng, "R-01", state)
        self.assertEqual(got["corridas"], [], "six headers closed a passagem")

    def test_the_record_of_this_passagem_covers_the_six(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.engagement(tmp)
            self.record(eng, tmp, "R-01")
            state = json.loads((eng / "_state.json").read_text(encoding="utf-8"))
            got = self.dash["lenses_for_round"](eng, "R-01", state)
            other = self.dash["lenses_for_round"](eng, "R-02", state)
        self.assertEqual(got["corridas"], SIX)
        self.assertEqual(got["em_falta"], [])
        self.assertTrue(got["fecha"])
        self.assertFalse(got["revista"], "closed as reviewed without a review")
        self.assertEqual(other["corridas"], [], "another passagem's record counted")
        self.assertFalse(other["fecha"])

    def test_reviewed_by_the_independent_reader(self):
        review = {"status": "completed",
                  "performed_by": {"kind": "agent", "name": "lens-coverage-reviewer"},
                  "method": "leitura", "completed_at": "2026-09-23T21:00:00Z",
                  "limitations": [],
                  "dimensions": {d: {"verdict": "treated", "note": "ok"} for d in SIX}}
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.engagement(tmp)
            self.record(eng, tmp, "R-01", review)
            state = json.loads((eng / "_state.json").read_text(encoding="utf-8"))
            got = self.dash["lenses_for_round"](eng, "R-01", state)
        self.assertTrue(got["fecha"] and got["revista"], got["motivos"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
