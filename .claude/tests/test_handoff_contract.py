# -*- coding: utf-8 -*-
"""handoff-v1 F1.6 — os contratos congelados em F1 existem, têm dono único e batem com os schemas.

- `library/kernel/handoff-contract.md` é dono do que o perfil acrescenta e nenhum outro
  contrato tem (FC, WP, índice, checkpoint, revisão, dependências); aponta para os donos
  existentes em vez de os repetir.
- `phases.md` diz as rotas de Options e os predicados de prontidão dentro de Decision (sem
  quinta fase, sem estado novo); `orchestration.md` admite o checkpoint e as dependências
  tipadas.
- Os campos do contrato funcional (plano 02 §7) e os ids (FC/J/WP) batem com o schema.
"""
import json
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
K = ROOT / "library" / "kernel"
HC = (K / "handoff-contract.md").read_text(encoding="utf-8")
PH = " ".join((K / "phases.md").read_text(encoding="utf-8").split())
OR = " ".join((K / "orchestration.md").read_text(encoding="utf-8").split())
W = runpy.run_path(str(K / "tools" / "workflow.py"))


class Contrato(unittest.TestCase):

    def test_every_schema_it_names_exists(self):
        for nome in ("handoff-state", "handoff-pack", "handoff-response", "handoff-work",
                     "handoff-functional", "handoff-index"):
            self.assertIn("`" + nome + "`", HC)
            self.assertTrue((K / "schemas" / (nome + ".schema.json")).is_file(), nome)

    def test_it_points_to_the_existing_owners_instead_of_restating_them(self):
        for dono in ("states.md", "phases.md", "orchestration.md", "blueprint-contract.md",
                     "coverage-contract.md", "render-contract.md"):
            self.assertIn("(" + dono + ")", HC, dono)

    def test_the_new_ids_match_the_schema_patterns(self):
        fc = W["load_schema"]("handoff-functional")["properties"]["items"]["items"]["properties"]
        self.assertEqual(fc["id"]["pattern"], "^FC-[0-9]{4}$")
        self.assertEqual(fc["journey_id"]["pattern"], "^J-[0-9]{4}$")
        for i in ("`FC-NNNN`", "`J-NNNN`", "`WP-NNNN`", "**are never reused**"):
            self.assertIn(i, HC)

    def test_the_functional_contract_fields_of_the_plan_are_in_the_schema(self):
        fc = W["load_schema"]("handoff-functional")["properties"]["items"]["items"]["properties"]
        for campo in ("purpose", "scope_id", "owner_role", "requirement_refs",
                      "architecture_refs", "authorization_ref", "actors", "preconditions",
                      "trigger", "inputs", "rule", "postconditions", "exceptions",
                      "acceptance_examples", "open_refs", "delegated_choices", "proof_refs",
                      "not_applicable", "semantic_origin"):
            self.assertIn(campo, fc, campo)

    def test_effort_has_one_owner(self):
        self.assertIn("Estimate (the only source of effort)", HC)
        self.assertIn("never a competing estimate", HC)


class Fases(unittest.TestCase):

    def test_options_follow_the_route(self):
        for r in ("`solution-choice`", "`platform-constrained`", "`change-impact`"):
            self.assertIn(r, PH)
        self.assertIn("a single viable candidate is admitted with its reason", PH)
        self.assertIn("with no artificial alternative technology", PH)

    def test_readiness_is_three_predicates_inside_decision_and_nothing_more(self):
        for p in ("`decision_ready`", "`design_ready`", "`handoff_ready`", "`integrity_ok`",
                  "`required_approvals_present`", "`receiver_review_complete`",
                  "`receiver_accepted`"):
            self.assertIn(p, PH)
        self.assertIn("not new SU states and not a fifth phase", PH)
        self.assertIn("An approval is a property of a revision and a scope", PH)


class Orquestracao(unittest.TestCase):

    def test_the_checkpoint_is_admitted_as_references_only(self):
        self.assertIn("`_work/checkpoint.json`", OR)
        self.assertIn("never a copy of their content, never a summary of what is known", OR)

    def test_typed_dependencies_are_admitted_for_handoff_v1(self):
        self.assertNotIn("never through a dependency graph or a new field", OR)
        self.assertIn("typed dependencies of `handoff-contract.md`", OR)


if __name__ == "__main__":
    unittest.main(verbosity=1)
