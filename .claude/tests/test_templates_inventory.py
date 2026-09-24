# -*- coding: utf-8 -*-
"""handoff-v1 F6.4 — os templates projectam o inventário; a estimativa cita WP e revisão.

Desenho: `docs/handoff-v1/F6/DESENHO.md` §4 (Q1, Q2). Contrato textual; a execução destas
regras é dos motores (`trace.py`, F6.2–F6.3) e o percurso de ponta a ponta é da F6.6
(T38 executável sobre `fx-hv1-05`).
"""
import re
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TPL = ROOT / "library" / "packs" / "pp" / "deliverable-templates"
SPEC = (TPL / "implementation-spec.template.md").read_text(encoding="utf-8")
EST = (TPL / "estimate.template.md").read_text(encoding="utf-8")
RENDER = (ROOT / ".claude" / "skills" / "aisa-render" / "SKILL.md").read_text(encoding="utf-8")
TR = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "trace.py"))
TT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_trace.py"))


def _rv():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "render_validate", ROOT / ".claude" / "hooks" / "render-validate.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def flat(s):
    sem = "\n".join(re.sub(r"^\s*>\s?", "", l) for l in s.splitlines())
    return re.sub(r"\s+", " ", sem)


class Especificacao(unittest.TestCase):

    def test_the_spec_owns_the_inventory_by_projecting_it(self):
        self.assertIn("_design/work-packages.json — the INVENTORY", SPEC)
        self.assertIn("never carries a duration", flat(SPEC))
        self.assertIn("### Inventário de trabalho (inventário r{{inventory_revision}})", SPEC)
        self.assertIn("| WP | Propósito | Realiza | Prova | Depende de | Aceitação | "
                      "Definição de feito |", SPEC)
        for slot in ("work_package_inventory", "inventory_revision"):
            self.assertIn("  - " + slot, SPEC.split("conditional_slots:")[1].split("#")[0])

    def test_the_scope_is_projected_with_its_authorised_exclusions(self):
        self.assertIn("_design/scope.json — the authorised scope", SPEC)

    def test_sequencing_is_the_inventory_dependencies(self):
        sec = flat(SPEC.split("## 14. Sequenciamento")[1].split("## 15.")[0])
        self.assertIn("as dependências são as `depends_on` do inventário", sec)

    def test_t38_migration_steps_cite_work_and_acceptance(self):
        sec = flat(SPEC.split("## 15. Migração e cutover")[1].split("## 16.")[0])
        self.assertIn("reconciliação, cutover, rollback e retenção/destino do legado **cada um** "
                      "cita o `WP-NNNN`", sec)
        self.assertIn("Um passo sem WP é item em aberto", sec)

    def test_a_projected_inventory_row_carries_no_duration(self):
        linha = "| WP-0001 | Submissão idempotente | FC-0001 | — | — | exemplo negativo | ok |"
        self.assertEqual(TR["spec_effort_check"](linha), [])


class Estimativa(unittest.TestCase):

    def test_mode_a_reads_the_inventory_file_at_the_cited_revision(self):
        bloco = flat(EST.split("input_inventory_authority:")[1].split("method_authority")[0])
        self.assertIn("Implementation Specification's inventory", bloco)
        self.assertIn("`_design/work-packages.json`", bloco)
        self.assertIn("`trace.py estimate-check` verifies", bloco)

    def test_one_line_per_wp_with_the_revision(self):
        sec = flat(EST.split("## 3. Decomposição de trabalho")[1].split("## 4.")[0])
        self.assertIn("**uma** linha por WP, nunca duas", sec)
        self.assertIn("`inventário r<N>`", sec)


class Render(unittest.TestCase):

    def test_render_runs_the_inventory_checks_before_a_real_version(self):
        sec = flat(RENDER.split("7c. **Inventory, estimate and scope gate")[1]
                   .split("8. Compute")[0])
        for cmd in ("trace.py show", "trace.py scope-gate", "trace.py estimate-check"):
            self.assertIn(cmd, sec)
        self.assertIn("Never adjust the inventory to make the estimate pass", sec)
        self.assertIn("step 7b/7c blocked it", RENDER)


class RenderValidate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.tmp = tempfile.TemporaryDirectory()
        cls.eng = TT["montado"](cls.tmp.name)
        (cls.eng / "_render").mkdir()
        cls.RV = _rv()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _gaps(self, deliverable, texto):
        f = self.eng / "_render" / "x_{}_v01.md".format(deliverable)
        f.write_text(texto, encoding="utf-8")
        return [(g["rule"], g["owner"]) for g in self.RV.inventory_gaps(self.eng, deliverable, f)]

    def test_the_spec_must_project_every_wp_without_duration(self):
        self.assertEqual(self._gaps("implementation-spec", "inventário r1\n| WP-0001 | a | — |\n"
                                    "| WP-0002 | b | — |\n"), [])
        self.assertIn(("EFFORT_IN_SPEC", "implementation"),
                      self._gaps("implementation-spec", "inventário r1\n| WP-0001 | 2 dias |\n"
                                 "| WP-0002 | b |\n"))
        self.assertIn(("MISSING_IN_SPEC", "implementation"),
                      self._gaps("implementation-spec", "inventário r1\n| WP-0001 | a |\n"))

    def test_the_estimate_must_cite_every_wp_once(self):
        self.assertIn(("UNESTIMATED_WP", "estimate"),
                      self._gaps("estimate", "| WP-0001 | 3 d |\ninventário r1\n"))


if __name__ == "__main__":
    unittest.main()
