# -*- coding: utf-8 -*-
"""handoff-v1 F5.4 — `/options` por rota, hooks por rota, sem conselho de personas.

Desenho: `docs/handoff-v1/F5/DESENHO.md` §4 (Q1, Q4).

    hooks   `phase-completeness` e o aviso de fase do `dashboard.py` contam as opções pela
            rota: três só em `solution-choice` (menos com o motivo); as outras admitem uma.
            Com perfil, pedem candidatos publicados, todos os mandatos recebidos e cada achado
            de um parecer corrente com disposição — não sete excertos de personas
    texto   o `/options` corre autor → publicar → router → mandato → revisor → receber →
            chairman, por esta ordem; nenhum passo lança personas
"""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CA = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_review_candidates.py"))
DI = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_review_dispositions.py"))
RV = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "review.py"))
D = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "dashboard.py"))
PC = runpy.run_path(str(ROOT / ".claude" / "hooks" / "phase-completeness.py"))
OPTIONS = (ROOT / ".claude" / "skills" / "aisa-options" / "SKILL.md").read_text(encoding="utf-8")


def linha(eng, prefixo):
    council, _v = PC["check_options"](eng, "O-01", "")
    return next(c for c in council if c[1].startswith(prefixo))


class ContagemPorRota(unittest.TestCase):

    def test_a_single_viable_candidate_passes_on_the_imposed_platform(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = CA["engagement"](tmp, "platform-constrained")
            CA["publish"](eng, CA["conjunto"](eng, [CA["cand"]("O-001")], **DI["IMPOSTA"]))
            self.assertTrue(linha(eng, "candidatos da rota")[0])
            g = D["_route_count_criterion"](eng, ["O-001"])
            self.assertTrue(g["ok"], g)
            self.assertIn("platform-constrained", g["criterion"])

    def test_solution_choice_needs_three_or_the_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = CA["engagement"](tmp)
            CA["publish"](eng, CA["conjunto"](eng, [CA["cand"]("O-001"), CA["cand"]("O-002")],
                                              reduction_reason="só duas aplicam"))
            self.assertTrue(linha(eng, "candidatos da rota")[0])
            self.assertTrue(D["_route_count_criterion"](eng, ["O-001", "O-002"])["ok"])
            p = eng / "_design" / "candidates.json"
            d = json.loads(p.read_text(encoding="utf-8"))
            d.pop("reduction_reason")
            p.write_text(json.dumps(d), encoding="utf-8")
            self.assertFalse(linha(eng, "candidatos da rota")[0])
            self.assertFalse(D["_route_count_criterion"](eng, ["O-001", "O-002"])["ok"])

    def test_the_historical_version_keeps_three(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp) / "velho"
            eng.mkdir()
            (eng / "_state.json").write_text(json.dumps({"phase": "options"}), encoding="utf-8")
            (eng / "options.md").write_text("### O-001\n", encoding="utf-8")
            self.assertEqual(linha(eng, "pelo menos 3")[1], "pelo menos 3 opcoes")
            self.assertEqual(linha(eng, "_council-prep")[1], "_council-prep 7/7 personas")
            self.assertEqual(D["_route_count_criterion"](eng, ["O-001"])["criterion"],
                             ">= 3 opções")


class RevisaoNoHook(unittest.TestCase):

    def test_mandates_received_and_findings_disposed(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = DI["dois"](tmp)
            council, _v = PC["check_options"](eng, "O-01", "")
            self.assertFalse([c for c in council if "personas" in c[1]])
            self.assertTrue(linha(eng, "candidatos publicados")[0])
            m = DI["mandato"](eng)
            self.assertFalse(linha(eng, "pareceres recebidos")[0])
            RV["receive"](eng, m["task_id"], DI["parecer"](m))
            self.assertTrue(linha(eng, "pareceres recebidos")[0])
            self.assertFalse(linha(eng, "achados dos pareceres")[0])
            RV["dispose"](eng, "REV-0001.F01", "escalated", "o dono decide", to="dono")
            self.assertTrue(linha(eng, "achados dos pareceres")[0])


class TextoDoOptions(unittest.TestCase):

    def test_the_steps_run_in_order(self):
        ordem = ["review.py draft-candidates", "review.py publish-candidates",
                 "review.py route", "review.py mandate", "`subagent_type`: `specialist-reviewer`",
                 "review.py receive", "Hand off to chairman-synthesis"]
        pos = [OPTIONS.index(x) for x in ordem]
        self.assertEqual(pos, sorted(pos))

    def test_no_step_launches_personas(self):
        for fora in ("Launch the 7 personas", "7 Task tool calls", "_council-prep/O-<NN>-<persona>",
                     "Council launch preamble"):
            self.assertNotIn(fora, OPTIONS)

    def test_the_route_table_is_in_the_skill(self):
        for rota in ("`solution-choice`", "`platform-constrained`", "`change-impact`"):
            self.assertIn(rota, OPTIONS)
        self.assertIn("no artificial shortlist of platforms", OPTIONS)


if __name__ == "__main__":
    unittest.main()
