# -*- coding: utf-8 -*-
"""handoff-v1 F7.2 — o stale derivado bloqueia a versão final (Q3), ponta a ponta.

Desenho: `docs/handoff-v1/F7/DESENHO.md` §1 (consumidores).

    T41   uma premissa de um FC do âmbito é respondida (`was`): o render final desse FC, o gate
          de âmbito e a prontidão do release recusam, com a cadeia até ao WP; o FC que não
          depende dela continua a poder sair; o `/status` diz o que rever
    saída republicar o FC com a sucessora muda o item e pede nova autorização; autorizado,
          a prontidão volta
    excl. um dependente de um item excluído informa, não bloqueia
"""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
RT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_release.py"))
AU = RT["AU"]
F = RT["F"]
R = RT["R"]
REL = RT["REL"]
TR = runpy.run_path(str(TOOLS / "trace.py"))
P = runpy.run_path(str(TOOLS / "projection.py"))
I = runpy.run_path(str(TOOLS / "impact.py"))


def _refs(eng, fc, refs):
    dr = F["draft"](eng)
    p = Path(dr["path"])
    d = json.loads(p.read_text(encoding="utf-8"))
    # Antes trocava aqui o sha do desenho, porque o `pronto` o retocava depois dos FC — a
    # troca de hash que a auditoria (A5) proíbe. O `pronto` revalida agora os FC.
    for it in d["items"]:
        if it["id"] == fc:
            it["requirement_refs"] = refs
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    F["publish"](eng, dr["draft"])


def _autoriza(eng, fcs, quando):
    RT["_decisao"](eng, F["authorization_block"](eng, fcs, AU["OWNER"], "SCOPE-0001",
                                                 timestamp=quando))


def com_premissa(tmp):
    """O pacote pronto, com o FC-0001 a assentar também na premissa A-001, autorizado. O FC
    mudou: o WP que o realiza é revalidado e a spec e a estimativa re-renderizadas (A3)."""
    eng = RT["pronto"](tmp)
    _refs(eng, "FC-0001", ["C-002", "C-003", "A-001"])
    _autoriza(eng, ["FC-0001"], "2026-09-24T09:00:00Z")
    _revalida_trabalho(eng, "FC-0001 passou a assentar também em A-001; a submissão não muda")
    return eng


def _revalida_trabalho(eng, porque):
    RT["IT"]["revalida_inventario"](eng, {"WP-0001": "still_valid"}, porque)
    RT["rerender"](eng)


def _responde_a001(eng):
    R["apply"](eng, row_id="A-001", answer_text="A chefia valida os urgentes em 4 horas",
               answered_by={"role": "responsável de compras"}, locator="answers.md#A-001")
    return I["su_rows"](eng)["A-001"]["resolved_to"][0]


class T41PontaAPonta(unittest.TestCase):

    def test_a_ready_package_with_the_premise_is_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = REL["readiness"](com_premissa(tmp))
            self.assertTrue(r["ready"], r["reasons"])

    def test_answering_the_premise_blocks_the_final_version_with_the_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = com_premissa(tmp)
            _responde_a001(eng)
            g = F["render_gate"](eng, ["FC-0001", "FC-0003"])
            self.assertFalse(g["final_allowed"])
            self.assertEqual([(b["code"], b["fc"]) for b in g["blocked"]
                              if b["code"] == "STALE_PREMISE"], [("STALE_PREMISE", "FC-0001")])
            self.assertTrue(F["render_gate"](eng, ["FC-0003"])["final_allowed"])
            sg = TR["scope_gate"](eng)
            self.assertEqual(sg["delivery"], "blocked")
            velhos = sorted(b["ref"] for b in sg["blockers"] if b["code"] == "STALE_PREMISE")
            self.assertEqual(velhos, ["FC-0001", "WP-0001"])
            wp = next(b for b in sg["blockers"] if b["ref"] == "WP-0001")
            self.assertIn("A-001 → FC-0001 → WP-0001", wp["detail"])
            r = REL["readiness"](eng)
            self.assertFalse(r["ready"])
            self.assertIn("2 dependente(s) sobre premissa mudada (STALE_PREMISE)", r["reasons"])
            self.assertEqual(REL["build"](eng)["delivery_level"], "preliminary")

    def test_status_names_what_to_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = com_premissa(tmp)
            _responde_a001(eng)
            st = P["operational_state"](eng)
            refs = {(v["ref"], v["blocks_final"]) for v in st["stale_dependents"]}
            self.assertIn(("FC-0001", True), refs)
            self.assertIn(("WP-0001", True), refs)
            txt = P["explain"](eng)["text"]
            self.assertIn("Assenta em premissas que mudaram", txt)
            self.assertIn("impede a versao final", txt)

    def test_republishing_with_the_successor_asks_for_a_new_authorisation(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = com_premissa(tmp)
            nova = _responde_a001(eng)
            _refs(eng, "FC-0001", ["C-002", "C-003", nova])
            # a premissa sai do FC; o FC mudou, logo o WP que o realiza fica por revalidar (A3)
            self.assertEqual([(f["code"], f["ref"]) for f in I["blocking"](eng)],
                             [("CONTRACT_CHANGED", "WP-0001")])
            auth = F["show"](eng)["items"]["FC-0001"]["authorization"]["state"]
            self.assertEqual(auth, "stale")
            self.assertFalse(REL["readiness"](eng)["ready"])
            _autoriza(eng, ["FC-0001"], "2026-09-24T10:00:00Z")
            self.assertFalse(REL["readiness"](eng)["ready"])        # o dono não revalida o WP
            _revalida_trabalho(eng, "a premissa passou a ser a sucessora; o trabalho não muda")
            r = REL["readiness"](eng)
            self.assertTrue(r["ready"], r["reasons"])

    def test_a_dependent_of_an_excluded_item_informs_and_does_not_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = RT["pronto"](tmp)
            R["apply"](eng, row_id="U-001", answer_text="Arredonda ao cêntimo por linha",
                       answered_by={"role": "responsável de compras"},
                       locator="answers.md#U-001")
            self.assertIn("FC-0002", I["stale"](eng)["affected"])
            self.assertEqual(I["blocking"](eng), [])
            self.assertNotIn("STALE_PREMISE",
                             [b["code"] for b in TR["scope_gate"](eng)["blockers"]])
            st = P["operational_state"](eng)
            self.assertIn(("FC-0002", False),
                          {(v["ref"], v["blocks_final"]) for v in st["stale_dependents"]})


if __name__ == "__main__":
    unittest.main()
