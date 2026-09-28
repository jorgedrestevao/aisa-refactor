# -*- coding: utf-8 -*-
"""handoff-v1 F3.4 — /frame pelo analista integrado + um revisor independente.

Desenho: `docs/handoff-v1/F3/DESENHO.md` §4 (Q4, Q5) e §0. O que se prova:

- o `/frame` já não lança as seis personas nem a ronda de antítese; lança um revisor, uma
  vez, depois da proposta;
- a síntese aplica as regras do chairman aos dois retornos (concordância não é evidência;
  divergência factual sem localizador → `Conflicted`; divergência de recomendação → dono);
- os hooks de fase lêem o perfil: `phase-completeness` pede a proposta e a revisão, e o
  aviso Discovery → Framing lê o registo `lens`, não seis ficheiros;
- o texto normativo diz quando um subagente se justifica.

Contrato textual onde é texto (limite declarado: não observa uma sessão); os hooks e o
motor são exercidos sobre engagements sintéticos.
"""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
FRAME = (ROOT / ".claude" / "skills" / "aisa-frame" / "SKILL.md").read_text(encoding="utf-8")
CHAIR = (ROOT / ".claude" / "skills" / "chairman-synthesis" / "SKILL.md").read_text(
    encoding="utf-8")
ORCH = (ROOT / "library" / "kernel" / "orchestration.md").read_text(encoding="utf-8")
REVIEWER = (ROOT / ".claude" / "agents" / "frame-reviewer.md").read_text(encoding="utf-8")
SIX = ["business", "operations", "user", "data", "governance", "financial"]


def flat(t):
    return " ".join(t.split())


class OFrameSemConselho(unittest.TestCase):

    def test_no_persona_is_launched_and_there_is_no_antithesis(self):
        for gone in ("Launch the 6 personas", "6 Task tool calls", "### 5b. Dialectic round",
                     "Concedo / Contesto", "_council-prep/F-<NN>-<persona>.md"):
            self.assertNotIn(gone, FRAME, gone)
        self.assertIn("Nothing else runs in Framing: no other role, no antithesis round.", FRAME)

    def test_one_reviewer_once_after_the_proposal(self):
        f = flat(FRAME)
        self.assertIn("subagent_type: frame-reviewer", f)
        self.assertIn("Launch **one** subagent", f)
        self.assertIn("in sequence, after the proposal exists", f)
        self.assertIn("F-<NN>-analyst.md", f)
        self.assertIn("F-<NN>-reviewer.md", f)
        self.assertIn("A frame that was not reviewed is never presented as reviewed", f)

    def test_the_reviewer_is_read_only_and_returns_findings(self):
        self.assertIn("tools: [Read, Grep, Glob]", REVIEWER)
        for campo in ("**Target**", "**Severity**", "**Kind**", "**Premise / evidence**",
                      "**Failure scenario**", "**Closing condition**",
                      "### Coverage of the review"):
            self.assertIn(campo, REVIEWER, campo)
        self.assertIn('"Looks fine" without the coverage lines closes nothing', REVIEWER)

    def test_recommendation_divergence_goes_to_the_owner(self):
        self.assertIn("*Usar a frase do revisor*", FRAME)
        self.assertIn("decided here, by the owner — never by the synthesis", flat(FRAME))


class ASinteseAplicaAsRegras(unittest.TestCase):

    def test_framing_inputs_carry_the_evidence_rules(self):
        sec = flat(CHAIR.split("## Framing inputs")[1].split("## Options inputs in a handoff-v1 engagement")[0])
        self.assertIn("Agreement is not evidence", sec)
        self.assertIn("`partes = analista∧revisor`", sec)
        self.assertIn("is not settled here", sec)
        self.assertIn("Step 2b does not run in Framing", sec)

    def test_the_dialectic_is_options_only(self):
        self.assertIn("Options only — in Framing this step does not run", CHAIR)
        dial = ORCH.split("## Dialectic round")[1].split("\n## ")[0]
        self.assertIn("retired in Framing", dial)


class TextoNormativo(unittest.TestCase):

    def test_orchestration_says_when_a_subagent_is_justified(self):
        o = flat(ORCH)
        self.assertIn("**When a subagent is justified**", o)
        self.assertIn("does **not** need the context of whoever launches it", o)
        self.assertIn("## Framing mode (handoff-v1 F3)", ORCH)
        self.assertIn("Discovery and Framing run no parallel subagents", o)

    def test_claude_md_principle_four(self):
        c = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertNotIn("council-independent (parallel subagents) in Framing/Options", c)
        self.assertIn("subagente só com benefício", c)

    def test_phases_framing_mode(self):
        p = (ROOT / "library" / "kernel" / "phases.md").read_text(encoding="utf-8")
        framing = p.split("## Phase 2: Framing")[1].split("## Phase 3")[0]
        self.assertIn("`analyst + reviewer`", framing)
        self.assertNotIn("parallel Task subagents; only the chairman", framing)


class HooksPorPerfil(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fix = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_migration.py"))
        cls.mig = runpy.run_path(str(TOOLS / "migrate.py"))
        cls.cov = runpy.run_path(str(TOOLS / "coverage.py"))
        cls.dash = runpy.run_path(str(TOOLS / "dashboard.py"))
        cls.pc = runpy.run_path(str(ROOT / ".claude" / "hooks" / "phase-completeness.py"))

    def engagement(self, tmp):
        projects = Path(tmp) / "projects"
        projects.mkdir()
        eng = Path(self.fix["make"](str(projects), self.fix["NOVO"]))
        self.mig["apply"](eng)
        return eng

    def set_round(self, eng, rnd):
        p = eng / "_state.json"
        st = json.loads(p.read_text(encoding="utf-8"))
        st["round"] = rnd
        p.write_text(json.dumps(st), encoding="utf-8")

    def record(self, eng, tmp, rnd):
        sk = self.cov["lens_skeleton"](eng, rnd)
        sk["generated_at"] = "2026-09-23T20:00:00Z"
        for d in SIX:
            sk["lens_coverage"]["dimensions"][d] = {
                "status": "assessed", "refs": ["C-001"], "justification": "base"}
        sk["lens_coverage"]["conflict_scan"] = {"refs": [], "note": "nenhum conflito"}
        p = Path(tmp) / "d.json"
        p.write_text(json.dumps(sk), encoding="utf-8")
        self.assertTrue(self.cov["finalize"](eng, p)["published"])

    def criterion(self, eng):
        g = self.dash["gate_state"](eng, "discovery→framing")
        return next(c for c in g["criteria"] if "perspectivas" in c["criterion"]
                    or "lentes" in c["criterion"])

    def test_gate_reads_the_lens_record_for_a_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.engagement(tmp)
            self.set_round(eng, "R-01")
            sem = self.criterion(eng)
            self.assertIn("registo lens", sem["criterion"])
            self.assertFalse(sem["ok"])
            self.record(eng, tmp, "R-01")
            com = self.criterion(eng)
            self.assertTrue(com["ok"], com)
            self.assertIn("por rever", com["value"])
            self.assertIn("actual", com["value"])

    def test_a_stale_record_stays_valid_and_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.engagement(tmp)
            self.set_round(eng, "R-01")
            self.record(eng, tmp, "R-01")
            su = eng / "shared-understanding.md"
            su.write_text(su.read_text(encoding="utf-8").replace(
                "Base partilhada", "Base partilhada e revista"), encoding="utf-8")
            c = self.criterion(eng)
            self.assertTrue(c["ok"])
            self.assertIn("desactualizado", c["value"])

    def test_the_historical_version_still_counts_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp) / "velho"
            eng.mkdir()
            (eng / "_state.json").write_text(json.dumps(
                {"engagement": "velho", "phase": "discovery", "round": "R-01"}),
                encoding="utf-8")
            (eng / "shared-understanding.md").write_text("# SU\n", encoding="utf-8")
            c = self.criterion(eng)
            self.assertIn("6 lentes", c["criterion"])

    def test_completeness_asks_for_analyst_and_reviewer_on_a_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = self.engagement(tmp)
            prep = eng / "lens-outputs" / "_council-prep"
            prep.mkdir(parents=True)
            council, _v = self.pc["check_framing"](eng, "F-01", "")
            linha = next(c for c in council if c[1].startswith("_council-prep"))
            self.assertEqual(linha[1], "_council-prep analista + revisor")
            self.assertFalse(linha[0])
            for n in ("analyst", "reviewer"):
                (prep / "F-01-{}.md".format(n)).write_text("x", encoding="utf-8")
            council, _v = self.pc["check_framing"](eng, "F-01", "")
            linha = next(c for c in council if c[1].startswith("_council-prep"))
            self.assertTrue(linha[0], linha)

    def test_completeness_keeps_six_personas_on_the_historical_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp) / "velho"
            eng.mkdir()
            (eng / "_state.json").write_text(json.dumps({"phase": "framing"}),
                                             encoding="utf-8")
            council, _v = self.pc["check_framing"](eng, "F-01", "")
            linha = next(c for c in council if c[1].startswith("_council-prep"))
            self.assertEqual(linha[1], "_council-prep 6/6 personas")


if __name__ == "__main__":
    unittest.main()
