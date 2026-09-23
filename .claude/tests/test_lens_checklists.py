# -*- coding: utf-8 -*-
"""handoff-v1 F3.2 — as seis perspectivas de Discovery vivem num ficheiro do kernel.

Desenho: `docs/handoff-v1/F3/DESENHO.md` §1 (Q1). `library/kernel/lens-checklists.md` é o
dono único das perguntas centrais (plano 03 → matriz de cobertura), das regras próprias de
cada perspectiva e da evidência de cobertura. As seis skills de lente de Discovery saíram;
`lens-technology` fica (Options).

Contrato textual, com o limite declarado: prova o que o ficheiro diz e que nenhuma
instrução viva aponta uma skill retirada. Não prova que o analista aplica as seis — isso é
a etapa `lens` do coverage (`test_coverage_lens.py`).
"""
import re
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KERNEL = ROOT / "library" / "kernel"
C = runpy.run_path(str(KERNEL / "tools" / "coverage.py"))
TEXT = (KERNEL / "lens-checklists.md").read_text(encoding="utf-8")
FLAT = " ".join(TEXT.split())

SECTIONS = {"business": "Business", "operations": "Operations", "user": "User",
            "data": "Data", "governance": "Governance", "financial": "Financial"}
RETIRED = tuple("lens-" + l for l in SECTIONS)
VENDORS = ("Power Platform", "Canvas App", "Model-driven", "Power Automate", "Dataverse",
           "OutSystems", "Mendix", "SharePoint")


def section(name):
    parts = re.split(r"^## ", TEXT, flags=re.M)
    body = next(p for p in parts if p.startswith(name + "\n"))
    return " ".join(body.split())


class UmFicheiroSeisPerspectivas(unittest.TestCase):

    def test_the_six_perspectives_are_the_coverage_dimensions(self):
        self.assertEqual(tuple(SECTIONS), C["LENS_DIMENSIONS"])
        for titulo in SECTIONS.values():
            self.assertIn("\n## {}\n".format(titulo), TEXT, titulo)

    def test_each_perspective_has_its_central_question_and_four_questions(self):
        for titulo in SECTIONS.values():
            s = section(titulo)
            self.assertIn("**Central question:**", s, titulo)
            for n in ("1. **", "2. **", "3. **", "4. **"):
                self.assertIn(n, s, titulo)
            self.assertIn("**Cues", s, titulo)
            self.assertIn("**Apply.**", s, titulo)

    def test_the_coverage_table_carries_the_plan_matrix(self):
        tabela = TEXT.split("## Coverage evidence")[1].split("\n## ")[0]
        for lente in SECTIONS:
            self.assertRegex(tabela, r"\| {} \| [^|]+\? \| [^|]+ \|".format(lente))
        for estado in C["LENS_STATUSES"]:
            self.assertIn("`{}`".format(estado), tabela)
        self.assertIn("**does not count**", tabela)
        self.assertIn("Without a reason it is invalid", tabela)

    def test_six_perspectives_are_not_six_documents(self):
        self.assertIn("never mean six documents or six executions", FLAT)
        self.assertNotIn("lens-outputs/", TEXT)

    def test_the_rules_live_in_the_kernel_once(self):
        self.assertEqual(TEXT.count("## Common rules"), 1)
        self.assertIn("the rule lives in `library/kernel/states.md` → *Admission of a question*",
                      FLAT)
        self.assertIn("*Confirmed threshold*", FLAT)
        for titulo in SECTIONS.values():
            self.assertNotIn("Admission", section(titulo), titulo)

    def test_as_is_and_to_be_stay_apart(self):
        """Plano F3 item 4: origem AS-IS vs proposta/decisão TO-BE (states.md → âmbito)."""
        for marca in ("`observed_as_is`", "`proposed_to_be`", "`authorized_to_be`"):
            self.assertIn(marca, TEXT)
        self.assertIn("A marker is not a state", FLAT)

    def test_no_vendor_before_options(self):
        for v in VENDORS:
            self.assertNotIn(v, TEXT, v)

    def test_cues_are_not_coverage(self):
        self.assertIn("an uncovered cue is not a gap and never becomes an `Unknown`", FLAT)


class RegrasProprias(unittest.TestCase):

    def test_operations_step_duration(self):
        s = section("Operations")
        self.assertIn("`step_duration` (P-5)", s)
        self.assertIn("Never a guessed figure", s)

    def test_data_shape(self):
        s = section("Data")
        self.assertIn("`data_shape` (P-5)", s)
        self.assertIn("never the attribute list", s)

    def test_governance_conflict_scan_runs_after_the_other_five(self):
        s = section("Governance")
        self.assertIn("**Conflict scan — after the other five.**", s)
        self.assertIn("**Never resolve a conflict silently**", s)
        self.assertIn("`conflict_scan`", s)
        self.assertIn("the governance **conflict scan** runs after all of them", FLAT)
        self.assertIn("never which person", s)

    def test_financial_funding_gate_and_baseline(self):
        s = section("Financial")
        self.assertIn("**only when `context.json.funding_gate` is `true`** (absent → `true`)", s)
        self.assertIn("these four are **inactive**", s)
        self.assertIn("volume × cycle time × loaded rate", s)
        self.assertIn("the baseline is written, not asked", s)


class SkillsRetiradas(unittest.TestCase):

    def test_the_six_discovery_lens_skills_are_gone_technology_stays(self):
        for nome in RETIRED:
            self.assertFalse((ROOT / ".claude" / "skills" / nome).exists(), nome)
        self.assertTrue((ROOT / ".claude" / "skills" / "lens-technology" / "SKILL.md").is_file())

    def test_no_live_instruction_points_at_a_retired_skill(self):
        vivos = [ROOT / "CLAUDE.md"]
        for pasta in ("skills", "agents", "commands", "hooks", "rules"):
            vivos += [p for p in (ROOT / ".claude" / pasta).rglob("*") if p.is_file()
                      and p.suffix in (".md", ".py", ".json")]
        vivos += [p for p in KERNEL.rglob("*.md")] + [p for p in KERNEL.rglob("*.py")]
        rx = re.compile(r"\b(?:{})\b".format("|".join(re.escape(n) for n in RETIRED)))
        falhas = []
        for p in vivos:
            for m in rx.finditer(p.read_text(encoding="utf-8", errors="replace")):
                falhas.append("{}: {}".format(p.relative_to(ROOT), m.group(0)))
        self.assertEqual(falhas, [])

    def test_the_retired_personas_left_their_memory_to_the_roles(self):
        # handoff-v1 F5.4 (Q4, Q7): the six Discovery personas are retired; their perspective
        # lives in this file (and the specialist roles), their memory under the analyst or role.
        mem = ROOT / ".claude" / "agent-memory" / "_universal"
        for agente, papel in (("business-analyst", "analyst"), ("operations-lead", "analyst"),
                              ("cfo-lens", "cost-estimate"), ("compliance-officer",
                                                              "security-operation"),
                              ("data-steward", "data-integration"), ("user-advocate",
                                                                     "ux-process")):
            self.assertFalse((ROOT / ".claude" / "agents" / (agente + ".md")).exists(), agente)
            self.assertTrue(list((mem / papel).glob("*.md")), papel)
        self.assertTrue(list((mem / "analyst").glob("business-analyst-*.md")))


if __name__ == "__main__":
    unittest.main()
