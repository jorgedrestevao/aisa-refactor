"""Agent wiring after the persona council (handoff-v1 F5.4).

The Phase E council checks (seven personas, a launch preamble, persona memory) are retired
with the council: Discovery and Framing run an integrated analyst plus one reviewer (F3),
Options an inline technical author plus the specialist reviewers the router selects (F5).
What survives is asserted here: each agent is an independent perspective with a mandate,
the return schema has one owner, the reviewers write nothing and see only what they are
given, the architect stays out of the pre-technology phases, and memory is bound by role.

    python .claude/tests/test_council_wiring.py
"""

import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RETIRED = ("business-analyst", "operations-lead", "user-advocate", "data-steward",
           "compliance-officer", "cfo-lens")
REVIEWERS = ("lens-coverage-reviewer", "frame-reviewer", "fc-reviewer", "specialist-reviewer")
SCHEMA_SECTIONS = (
    "### Headline",
    "### Evidence anchors",
    "### Proposal",
    "### Open questions / Unknowns flagged",
    "### Conflicts seen",
    "### Risks",
)


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


AGENTS_DIR = os.path.join(ROOT, ".claude", "agents")
FRAME = read(".claude", "skills", "aisa-frame", "SKILL.md")
OPTIONS = read(".claude", "skills", "aisa-options", "SKILL.md")
RETRO = read(".claude", "skills", "aisa-retro", "SKILL.md")
CHAIRMAN = read(".claude", "skills", "chairman-synthesis", "SKILL.md")
ORCH = read("library", "kernel", "orchestration.md")
ARCHITECT = read(".claude", "agents", "solution-architect.md")
SPECIALIST = read(".claude", "agents", "specialist-reviewer.md")
SCHEMA = CHAIRMAN.split("## Return schema (canonical)")[1].split("\n## Hard rules")[0]


class TestThePersonaCouncilIsRetired(unittest.TestCase):
    def test_no_persona_agent_remains(self):
        for name in RETIRED:
            self.assertFalse(os.path.exists(os.path.join(AGENTS_DIR, name + ".md")), name)

    def test_no_skill_launches_personas(self):
        for name, text in (("aisa-options", OPTIONS), ("aisa-retro", RETRO),
                           ("aisa-frame", FRAME)):
            for persona in RETIRED:
                self.assertNotIn("`" + persona + "`,", text, name + " still lists " + persona)
            self.assertNotIn("Launch the 7 personas", text, name)
        self.assertNotIn("## Council launch preamble", CHAIRMAN)
        self.assertNotIn("## Council-independent mode", ORCH)

    def test_orchestration_declares_the_options_mode(self):
        self.assertIn("## Options mode (handoff-v1 F5)", ORCH)
        self.assertIn("**Agent = independent perspective + mandate.**", ORCH)


class TestReviewersAreIndependentAndReadOnly(unittest.TestCase):
    def test_every_reviewer_has_read_only_tools(self):
        for name in REVIEWERS:
            text = read(".claude", "agents", name + ".md")
            self.assertIn("tools: [Read, Grep, Glob]", text, name)

    def test_the_specialist_sees_only_its_mandate(self):
        self.assertIn("The invocation gives you one path: the mandate", SPECIALIST)
        self.assertIn("Read only what the mandate lists", SPECIALIST)
        self.assertIn("do not see what any other reviewer said", SPECIALIST)
        self.assertIn("the engagement root and the mandate path — nothing else", OPTIONS)

    def test_the_specialist_returns_the_output_contract(self):
        for key in ("task_id", "input_revision", "coverage", "findings", "assumptions",
                    "unanswered", "recommended_actions", "sources_used"):
            self.assertIn('"' + key + '"', SPECIALIST, key)
        self.assertIn("Concedo / Contesto / Síntese proposta", SPECIALIST)

    def test_reviewers_run_after_publication(self):
        self.assertIn("No reviewer runs before this", OPTIONS)
        self.assertIn("published **before** the reviewer runs", OPTIONS)


class TestReturnSchemaHasOneOwner(unittest.TestCase):
    def test_schema_lives_once_in_chairman_synthesis(self):
        self.assertEqual(CHAIRMAN.count("## Return schema (canonical)"), 1)
        for section in SCHEMA_SECTIONS:
            self.assertIn(section, SCHEMA, "schema missing " + section)
        self.assertIn("*Return schema* → the six sections", FRAME)

    def test_no_agent_copies_the_schema(self):
        for name in os.listdir(AGENTS_DIR):
            text = read(".claude", "agents", name)
            for section in SCHEMA_SECTIONS:
                self.assertNotIn(section, text, name + " copies the return schema")

    def test_chairman_parses_the_schema_it_owns(self):
        self.assertIn("Parse the six sections", CHAIRMAN)
        self.assertIn("- (none)", SCHEMA)


class TestPhaseBoundaries(unittest.TestCase):
    def test_framing_stays_technology_neutral(self):
        self.assertIn("Framing is pre-technology — no vendor or product names", FRAME)
        self.assertIn("no vendor or product names",
                      read(".claude", "agents", "frame-reviewer.md").lower())

    def test_solution_architect_is_not_launched_in_framing(self):
        self.assertIn("solution-architect is NOT invoked in Framing", FRAME)
        self.assertIn("**Framing**: **not invoked**", ARCHITECT)
        self.assertIn("## Phase gate", ARCHITECT)

    def test_the_architect_authors_inline_and_pulls_the_pack(self):
        self.assertIn("inline, not as a Task subagent", OPTIONS)
        self.assertIn("Pack knowledge is pull-based", ARCHITECT)
        self.assertIn("Never load the domain-knowledge base by default", ARCHITECT)
        self.assertIn("receives no Discovery `extra_signals`", OPTIONS)


class TestMemoryByRole(unittest.TestCase):
    def test_the_architect_reads_its_role_memory(self):
        self.assertIn("_universal/architect/", ARCHITECT)
        self.assertIn("_tenant/<tenant>/architect/", ARCHITECT)

    def test_retro_writes_by_role_after_curation(self):
        self.assertIn(".claude/agent-memory/_universal/<role>/diary.md", RETRO)
        self.assertIn("NUNCA escrever em agent-memory sem aprovação humana", RETRO)

    def test_a_reviewer_gets_memory_only_through_its_mandate(self):
        self.assertIn("files of your role's memory", SPECIALIST)
        spec = read("library", "kernel", "specialists.md")
        self.assertIn("never another role's", spec)


if __name__ == "__main__":
    unittest.main(verbosity=2)
