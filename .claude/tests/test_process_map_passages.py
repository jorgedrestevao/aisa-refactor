"""process-map M5.1 — nenhum parágrafo de uma fonte curta desaparece em silêncio.

Piloto M5: uma exceção operacional citada textualmente pelo dono numa nota curta ficou
fora do mapa (v02), e nem o `check`, nem a revisão das fontes, nem a validação a apanharam —
o process-model citava os parágrafos numa linha sem etiqueta e o mapa não os citava. Agora,
cada parágrafo com conteúdo de uma fonte de texto curta (extracção LT `ok`, até
`PASSAGE_LIMIT` parágrafos, sem transcrições com tempo) tem de estar citado num elemento ou
disposto em `orphans`; senão `MAP-PASSAGE-UNPLACED` recusa a publicação.

    python .claude/tests/test_process_map_passages.py
"""
import json
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_process_map_core.py"), run_name="helpers")
P = C["P"]
NOTA = "_capture/nota.md.text.md"


def _fonte(cap: Path, name: str, paras: list, fmt: str = ".md", status: str = "ok"):
    lines = ["<!-- aisa.capture.text-extraction -->", "# Source: {}".format(name), ""]
    for i, body in enumerate(paras, 1):
        lines += ["[¶{}] {}".format(i, body), ""]
    (cap / (name + ".text.md")).write_text("\n".join(lines), encoding="utf-8")
    stem = name.rsplit(".", 1)[0]
    (cap / (stem + ".extraction.json")).write_text(json.dumps({
        "artefact": "aisa.capture.text-extraction", "status": status,
        "identity": {"filename": name, "format": fmt},
        "units": {"unit": "paragraph", "paragraphs": len(paras)},
        "output": {"text_md": name + ".text.md"}}), encoding="utf-8")


class Base(C["Base"]):

    def setUp(self):
        super().setUp()
        self.cap = self.eng / "_capture"
        _fonte(self.cap, "nota.md", ["Data: 2026-09-18", ">",
                                     "O ficheiro já se estragou várias vezes.",
                                     "Só uma pessoa o sabe recuperar."])

    def codes(self, d):
        return {e["code"] for e in P["check"](self.eng, self.stamped(d))["errors"]}

    def unplaced(self, d):
        return [e["message"] for e in P["check"](self.eng, self.stamped(d))["errors"]
                if e["code"] == P["MAP_PASSAGE_UNPLACED"]]


class ParagrafoSemDestino(Base):

    def test_an_uncited_paragraph_refuses_the_map_and_is_named(self):
        msgs = self.unplaced(C["draft_v1"]())
        self.assertEqual(len(msgs), 1)
        self.assertIn("¶1", msgs[0])
        self.assertIn("¶3–4", msgs[0])
        self.assertNotIn("¶2", msgs[0], "um parágrafo sem conteúdo (só `>`) não é unidade")

    def test_a_range_anchor_covers_every_paragraph_it_spans(self):
        d = C["draft_v1"]()
        d["nodes"][1]["evidence"].append({"ref": NOTA + "#¶3–4"})
        d["orphans"] = [{"ref": NOTA + "#¶1", "reason": "out_of_scope",
                         "materiality": "not-material", "note": "metadados da nota"}]
        self.assertNotIn(P["MAP_PASSAGE_UNPLACED"], self.codes(d))
        self.assertTrue(self.publish(self.stamped(d))["published"])

    def test_a_range_with_a_missing_paragraph_does_not_resolve(self):
        r = P["resolve_ref"](self.eng, NOTA + "#¶3–9")
        self.assertEqual(r["status"], "unresolved")

    def test_a_single_paragraph_keeps_its_digest(self):
        r = P["resolve_ref"](self.eng, NOTA + "#¶3")
        self.assertEqual(r["units"], [NOTA + "#¶3"])
        self.assertEqual(r["digest"], P["_sha_text"](
            "[¶3] O ficheiro já se estragou várias vezes."),
            "o digest de uma âncora simples não muda: mapas já publicados continuam actuais")

    def test_a_material_exclusion_still_needs_an_authority(self):
        d = C["draft_v1"]()
        d["orphans"] = [{"ref": NOTA + "#¶1–4", "reason": "out_of_scope",
                         "materiality": "material", "note": "fora do projecto"}]
        c = self.codes(d)
        self.assertNotIn(P["MAP_PASSAGE_UNPLACED"], c)
        self.assertIn(P["MAP_ORPHAN_NO_AUTHORITY"], c)


class OQueNaoSeVerifica(Base):

    def test_timed_transcripts_and_failed_extractions_are_not_itemised(self):
        _fonte(self.cap, "reuniao.vtt", ["fala sem destino"], fmt=".vtt")
        _fonte(self.cap, "partido.pdf", ["texto sem destino"], fmt=".pdf", status="partial")
        keys = P["passage_units"](self.eng)["units"]
        self.assertFalse([k for k in keys if "reuniao" in k or "partido" in k])

    def test_a_long_source_is_an_explicit_gap_not_a_silent_pass(self):
        _fonte(self.cap, "manual.docx", ["parágrafo {}".format(i)
                                         for i in range(P["PASSAGE_LIMIT"] + 1)], fmt=".docx")
        v = P["check"](self.eng, self.stamped(C["draft_v1"]()))
        gaps = [g for g in v["gaps"] if g["code"] == "MAP-SOURCE-UNITEMIZED"]
        self.assertEqual(len(gaps), 1)
        self.assertIn("manual.docx", gaps[0]["message"])

    def test_the_verdict_counts_the_passages(self):
        v = P["check"](self.eng, self.stamped(C["draft_v1"]()))
        self.assertEqual(v["passages"]["units"], 3)
        self.assertEqual(v["passages"]["missing"], [NOTA + "#¶1", NOTA + "#¶3", NOTA + "#¶4"])


if __name__ == "__main__":
    unittest.main()
