# -*- coding: utf-8 -*-
"""handoff-v1 F4.4 — o passo funcional do `/blueprint` e o revisor `fc-reviewer`.

Desenho: `docs/handoff-v1/F4/DESENHO.md` §4 (Q1, Q5). Contrato textual, com o limite
declarado: prova o que a skill manda fazer e que os comandos que nomeia existem no motor;
o comportamento do motor está em `test_functional_*`. Não observa uma sessão.
"""
import re
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = (ROOT / ".claude" / "skills" / "aisa-blueprint" / "SKILL.md").read_text(encoding="utf-8")
FLAT = " ".join(SKILL.split())
AGENT = (ROOT / ".claude" / "agents" / "fc-reviewer.md").read_text(encoding="utf-8")
F = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "functional.py"))


class PassoFuncional(unittest.TestCase):

    def test_the_step_sits_after_coverage_and_before_the_output(self):
        self.assertLess(SKILL.index("13b. **Coverage"), SKILL.index("13c. **Functional contracts"))
        self.assertLess(SKILL.index("13c. **Functional contracts"), SKILL.index("14. **Output**"))
        self.assertIn("Skip in draft mode", SKILL.split("13c.")[1][:400])

    def test_every_command_the_skill_names_exists_in_the_motor(self):
        nomes = set(re.findall(r"functional\.py ([a-z-]+)", SKILL))
        self.assertTrue({"draft", "check", "publish", "show", "authorization-block",
                         "conflicts"} <= nomes, nomes)
        # handoff-v1 F6.3: os comandos que o motor declara no argparse, lidos do motor
        motor = (ROOT / "library" / "kernel" / "tools" / "functional.py").read_text(
            encoding="utf-8")
        bloco = motor.split('ap.add_argument("command", choices=[', 1)[1].split("]", 1)[0]
        escolhas = set(re.findall(r'"([a-z-]+)"', bloco))
        self.assertEqual(nomes - escolhas, set())

    def test_no_gap_is_filled_and_no_side_is_picked(self):
        self.assertIn("never fill the gap to make it pass", FLAT)
        self.assertIn("Never pick a side", FLAT)
        self.assertIn("`partes = desenho∧contrato funcional`", FLAT)

    def test_one_reviewer_after_publication_with_fresh_context(self):
        self.assertIn("`subagent_type: fc-reviewer`", FLAT)
        self.assertIn("Launch **one** subagent", FLAT)
        self.assertIn("A review of an earlier revision does not cover this one", FLAT)

    def test_approval_checks_functional_coherence(self):
        self.assertIn("run **three** mechanical checks", FLAT)
        self.assertIn("**(iii) Functional coherence**", FLAT)

    def test_only_the_owner_authorizes_through_the_motor_block(self):
        s16 = " ".join(SKILL.split("16. **Authorising functional contracts**")[1]
                       .split("## Domain Knowledge")[0].split())
        self.assertIn("never an agent", SKILL.split("16. **Authorising")[1][:120])
        self.assertIn("`AskUserQuestion`", s16)
        self.assertIn("never by hand", s16)
        self.assertIn("the `Assumed` rows stay `Assumed`", s16)

    def test_behaviour_lives_in_the_contracts(self):
        self.assertIn("11. **Behaviour lives in the functional contracts, not in the design.**",
                      SKILL)


class Revisor(unittest.TestCase):

    def test_read_only_and_returns_findings(self):
        self.assertIn("tools: [Read, Grep, Glob]", AGENT)
        for campo in ("**Target**", "**Severity**", "**Premise / evidence**",
                      "**Failure scenario**", "**Closing condition**",
                      "### Coverage of the review"):
            self.assertIn(campo, AGENT)
        self.assertIn("never authorise", AGENT)
        self.assertIn('"Looks fine" without the coverage lines closes nothing', AGENT)


if __name__ == "__main__":
    unittest.main()
