# -*- coding: utf-8 -*-
"""handoff-v1 F7.1 — raio de impacto e stale derivado (impact.py).

Desenho: `docs/handoff-v1/F7/DESENHO.md` §1 (Q1–Q3).

    publicação  FC, âmbito, inventário e candidatos registam em `based_on` a impressão de
                cada linha citada (`state`, `criticidade`, `resolved`, retirada)
    T41         uma premissa que muda (resposta, retirada, estado/criticidade no sítio) marca
                os dependentes reais, com a cadeia, transitivamente FC → WP e candidato →
                parecer; o que não depende fica de fora
    T42         texto editado no sítio, `verificado_em` renovado ou unidade do pack que o
                mandato não consumiu → nada reabre; a revisão de bytes continua exacta
    Q1          nada se escreve: o motor só lê
"""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
TT = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_trace.py"))
IT = TT["IT"]
I = runpy.run_path(str(TOOLS / "impact.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
F = TT["F"]
SU = "shared-understanding.md"


def codes(r):
    return sorted({(f["code"], f["ref"]) for f in r["findings"]})


def _linha(eng, rid, old, new):
    """Edição no sítio de uma célula da linha `rid` (fixture: simula uma edição directa
    depois reconciliada — o motor não sabe por que caminho chegou)."""
    p = eng / SU
    out = []
    for ln in p.read_text(encoding="utf-8").splitlines(keepends=True):
        if ln.startswith("| {} |".format(rid)):
            assert old in ln, (rid, old)
            ln = ln.replace(old, new, 1)
        out.append(ln)
    p.write_text("".join(out), encoding="utf-8", newline="\n")


def _move(eng, rid, section):
    """Mudança de estado no sítio: a linha passa, com o mesmo id, para outra secção (fixture:
    uma edição directa depois reconciliada)."""
    p = eng / SU
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    row = next(ln for ln in lines if ln.startswith("| {} |".format(rid)))
    lines.remove(row)
    i = lines.index("## {}\n".format(section))
    lines.insert(i + 2, row)
    p.write_text("".join(lines), encoding="utf-8", newline="\n")


def _responde(eng, rid="U-001"):
    return R["apply"](eng, row_id=rid, answer_text="Arredonda ao cêntimo, metade para cima",
                      answered_by={"role": "dono do processo"}, locator="answers.md#" + rid)


class Impressao(unittest.TestCase):

    def test_the_publication_records_the_basis_of_each_cited_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            fc = json.loads((eng / "_design/functional-contracts.json").read_text("utf-8"))
            rows = {b["ref"]: b for b in fc["based_on"] if "#" in b["ref"]}
            self.assertEqual(sorted(rows), [SU + "#C-002", SU + "#C-003", SU + "#C-004",
                                            SU + "#U-001"])
            self.assertEqual(rows[SU + "#U-001"]["row"],
                             {"state": "Unknown", "criticidade": "Critical",
                              "resolved": False, "retired": False})
            cand = json.loads((eng / "_design/candidates.json").read_text("utf-8"))
            self.assertIn(SU + "#C-004", [b["ref"] for b in cand["based_on"]])
            r = I["stale"](eng)
            self.assertEqual((r["stale"], r["unverified"]), (False, []))

    def test_only_exact_references_count_never_prose(self):
        self.assertEqual(I["cited_rows"]({"rule": "ver C-002 e U-001", "refs": [
            "C-002", "shared-understanding.md#U-001", "frame.md#C-003", "#A-001"]}),
            ["A-001", "C-002", "U-001"])


class T41(unittest.TestCase):

    def test_an_answer_marks_its_real_dependents_and_spares_the_rest(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = TT["wps"]() + [IT["wp"]("WP-0003", purpose="Valor",
                                            realizes=["FC-0002"])]
            eng = TT["montado"](tmp, items=items)
            antes = {p: p.read_bytes() for p in (eng / "_design").rglob("*") if p.is_file()}
            _responde(eng)
            r = I["stale"](eng)
            self.assertEqual(codes(r), [("ROW_RESOLVED", "FC-0002"),
                                        ("VIA_CONTRACT", "WP-0003")])
            via = next(f for f in r["findings"] if f["code"] == "VIA_CONTRACT")
            self.assertEqual(via["chain"], ["U-001", "FC-0002", "WP-0003"])
            self.assertTrue(via["excluded"])
            self.assertNotIn("FC-0001", r["affected"])
            self.assertEqual({p: p.read_bytes() for p in (eng / "_design").rglob("*")
                              if p.is_file()}, antes)           # Q1: nada se escreve

    def test_a_withdrawal_is_a_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            R["apply_withdraw"](eng, row_id="U-001", reason="fora do processo")
            self.assertEqual(codes(I["stale"](eng)), [("ROW_WITHDRAWN", "FC-0002")])

    def test_criticality_changed_in_place_is_seen_through_the_recorded_basis(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            _linha(eng, "U-001", "| Critical |", "| Med |")
            r = I["stale"](eng)
            self.assertEqual(codes(r), [("ROW_CHANGED", "FC-0002")])
            self.assertIn("criticidade Critical → Med", r["findings"][0]["detail"])

    def test_republishing_records_no_semantic_impact_and_keeps_the_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            _linha(eng, "U-001", "| Critical |", "| Med |")
            antes = F["show"](eng)["items"]["FC-0002"]["sha256"]
            dr = F["draft"](eng)
            F["publish"](eng, dr["draft"])
            self.assertEqual(I["stale"](eng)["findings"], [])
            self.assertEqual(F["show"](eng)["items"]["FC-0002"]["sha256"], antes)

    def test_a_candidate_premise_reaches_the_reviews_of_that_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            # o estado de uma linha é a secção; com o mesmo id noutra secção a SU já não a lê
            # como linha (prefixo ≠ estado) — para o dependente, a premissa desapareceu
            _move(eng, "C-004", "Assumed")
            r = I["stale"](eng)
            got = codes(r)
            for dep in ("FC-0003", "O-001", "O-002"):
                self.assertIn(("ROW_MISSING", dep), got)
            self.assertIn(("VIA_CONTRACT", "WP-0002"), got)
            self.assertIn(("VIA_CANDIDATE", "REV-0001"), got)
            self.assertNotIn("WP-0001", r["affected"])

    def test_a_design_node_citing_a_missing_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            p = eng / IT["BP"]
            p.write_text(p.read_text(encoding="utf-8").replace("su_refs: [C-005]",
                                                              "su_refs: [C-099]", 1),
                         encoding="utf-8")
            r = I["stale"](eng)
            miss = [f for f in r["findings"] if f["code"] == "ROW_MISSING"]
            self.assertEqual([f["cause"] for f in miss], ["C-099"])
            self.assertTrue(miss[0]["ref"].startswith(IT["BP"] + "#"))

    def test_an_artefact_without_basis_still_sees_resolution_and_says_it_is_unverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            p = eng / "_design/functional-contracts.json"
            d = json.loads(p.read_text(encoding="utf-8"))
            d["based_on"] = [b for b in d["based_on"] if "#" not in b["ref"]]
            p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            r = I["stale"](eng)
            self.assertIn({"ref": "FC-0001", "row": "C-002",
                           "artefact": "_design/functional-contracts.json"}, r["unverified"])
            _responde(eng)
            self.assertIn(("ROW_RESOLVED", "FC-0002"), codes(I["stale"](eng)))

    def test_the_radius_before_publishing(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            r = I["impact"](eng, ["C-004"])
            self.assertEqual(r["affected"], ["FC-0003", "O-001", "O-002", "REV-0001",
                                             "REV-0002", "REV-0003", "WP-0002"])
            self.assertIn("FC-0001", r["unaffected"])
            self.assertIn("WP-0001", r["unaffected"])


class T42(unittest.TestCase):

    def test_an_editorial_edit_reopens_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            _linha(eng, "U-001", "|", "| ")                   # espaço a mais: só redacção
            _linha(eng, "C-004", "| C-004 |", "| C-004 | ")
            r = I["stale"](eng)
            self.assertEqual((r["stale"], r["findings"]), (False, []))

    def test_revalidation_is_not_a_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            R["apply_revalidate"](eng, row_id="C-004", still_holds=True,
                                  note="continua a valer", by="role: dono | fonte: reunião")
            self.assertEqual(I["stale"](eng)["findings"], [])

    def test_the_byte_revision_stays_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            p = eng / IT["BP"]
            p.write_text(p.read_text(encoding="utf-8") + "\n# nota editorial\n",
                         encoding="utf-8")
            r = I["stale"](eng)
            b = [x for x in r["bytes"] if x["ref"] == IT["BP"]]
            self.assertTrue(b and b[0]["changed"] and b[0]["recorded"] != b[0]["now"])
            self.assertEqual(r["findings"], [])

    def test_only_a_consumed_knowledge_unit_reaches_its_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = TT["montado"](tmp)
            self.assertEqual(I["stale"](eng)["findings"], [])  # o resto do pack não conta
            mandatos = sorted((eng / "_design/reviews").glob("REV-*.mandate.json"))
            com = [p for p in mandatos
                   if json.loads(p.read_text(encoding="utf-8")).get("knowledge_refs")]
            self.assertTrue(com, "a fixture tem de ter um mandato com conhecimento")
            # fixture: simula a unidade consumida a mudar depois do mandato
            m = json.loads(com[0].read_text(encoding="utf-8"))
            m["knowledge_refs"][0]["sha256"] = "0" * 64
            com[0].write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
            r = I["stale"](eng)
            self.assertEqual(codes(r), [("KNOWLEDGE_CHANGED", m["task_id"])])


if __name__ == "__main__":
    unittest.main()
