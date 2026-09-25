"""process-map M2 — o mapa nasce da captura e mostra-se como é.

Casos (docs/process-map/PLANO.md §15): MAP-24 (mesmo input → mesmos bytes; rótulo com
HTML/script escapado), MAP-07 (um órfão material por avaliar publica-se, fica à vista e não
conta como resolvido), texto sem Excel, Excel com extracção incompleta (o estado falhado
fica à vista), o render não depende da aprovação para mostrar incompletude, e a ligação das
skills (passos 5d/5e da captura, aviso no início de `/round`).

    python .claude/tests/test_process_map_capture.py
"""
import json
import runpy
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_process_map_core.py"), run_name="helpers")
P = C["P"]
CAPTURE = (ROOT / ".claude" / "skills" / "aisa-capture" / "SKILL.md").read_text(encoding="utf-8")
ROUND = (ROOT / ".claude" / "skills" / "aisa-round" / "SKILL.md").read_text(encoding="utf-8")
GUIDE = ROOT / "library" / "kernel" / "capture-templates" / "process-map.guide.md"


class Base(C["Base"]):

    def published(self, change=None):
        d = C["draft_v1"]()
        if change:
            change(d)
        d = self.stamped(d)
        r = self.publish(d)
        self.assertTrue(r["published"], r.get("verdict"))
        return d


class MAP24_RenderDeterminista(Base):

    def test_the_same_input_renders_the_same_bytes(self):
        self.published()
        a = P["render"](self.eng).read_bytes()
        (self.eng / "process-map.html").unlink()
        b = P["render"](self.eng).read_bytes()
        self.assertEqual(a, b)
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        copy = Path(other.name) / "novo"
        shutil.copytree(self.eng, copy)
        self.assertEqual(P["render_html"](copy).encode("utf-8"), a,
                         "o caminho do engagement entrou nos bytes")

    def test_labels_are_escaped_and_nothing_from_the_source_runs(self):
        evil = '<script>alert("x")</script> & "aspas"'

        def poison(d):
            d["nodes"][1]["label"] = evil
            d["lanes"][0]["label"] = "<b>Fixador</b>"
            d["edges"][0]["label"] = "<img src=x onerror=alert(1)>"
        self.published(poison)
        html = P["render_html"](self.eng)
        self.assertNotIn("<script>alert", html)
        self.assertNotIn("<img src=x", html)
        self.assertNotIn("<b>Fixador</b>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script", html.lower().replace("&lt;script", ""),
                         "a página não leva script nenhum")

    def test_the_page_is_self_contained_with_both_themes(self):
        self.published()
        html = P["render_html"](self.eng)
        for banned in ("<link", "src=\"http", "@import", "<script"):
            self.assertNotIn(banned, html)
        self.assertIn("prefers-color-scheme: dark", html)
        self.assertIn(':root[data-theme="dark"]', html)
        self.assertIn("<svg", html)

    def test_no_map_no_page(self):
        with self.assertRaises(ValueError):
            P["render_html"](self.eng)


class IncompletudeVisivel(Base):

    def test_every_node_edge_and_doubt_is_in_the_page_without_approval(self):
        self.published()
        html = P["render_html"](self.eng)
        m = P["load"](self.eng)["map"]
        for n in m["nodes"]:
            self.assertIn(n["id"], html)
        for e in m["edges"]:
            self.assertIn(e["id"], html)
        self.assertIn("por validar", html)
        self.assertIn("Quem consome o resumo ao fim de semana?", html)

    def test_many_nodes_are_all_drawn_no_numeric_cap(self):
        def many(d):
            for i in range(4, 44):
                d["nodes"].append({"id": "MAPN-{:03d}".format(i), "kind": "step",
                                   "label": "passo {}".format(i), "lane": "MAPL-001",
                                   "order": i, "marker": "OBSERVED",
                                   "evidence": [{"ref": "_capture/process-model.md#PM-001"}]})
        self.published(many)
        svg = P["render_svg"](P["load"](self.eng)["map"])
        self.assertEqual(svg.count('class="numt"'), 43)


class MAP07_OrfaoMaterial(Base):

    def test_a_material_undetermined_orphan_publishes_and_stays_open(self):
        def orphan(d):
            d["details"] = d["details"][:1]
            d["orphans"] = [{"ref": "_capture/precos-2024.xlsx.calc-chain.json#CALC-001",
                             "reason": "undetermined", "materiality": "material",
                             "note": "não se sabe se o cálculo de 2024 ainda se usa"}]
        d = self.stamped()
        orphan(d)
        v = P["check"](self.eng, self.stamped(d))
        self.assertTrue(v["valid"], v["errors"])
        self.assertIn("MAP-ORPHAN-OPEN", {g["code"] for g in v["gaps"]})
        self.assertTrue(self.publish(self.stamped(d))["published"])
        html = P["render_html"](self.eng)
        self.assertIn("por avaliar", html)
        self.assertIn("não se sabe se o cálculo de 2024 ainda se usa", html)
        r = self.cli("check", "--engagement", "novo", "--draft",
                     str(self.save(self.stamped(d) | {"base": P["load"](self.eng)["digest"]})))
        self.assertEqual(r.returncode, 4, "um órfão material aberto não pode dar exit 0")


class TextoSemExcel(unittest.TestCase):

    def test_a_text_only_engagement_gets_a_map_from_its_passages(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        eng = C["L"]["novo"](base)
        cap = eng / "_capture"
        cap.mkdir()
        (cap / "process-model.md").write_text(C["PROCESS_MODEL"].replace(
            "CALC-001 copiado do motor.", "calc-chain: absent (no structured source)"),
            encoding="utf-8")
        (cap / "notas.docx.text.md").write_text(
            "# notas.docx\n\n¶3 O resumo diário vai por e-mail aos comerciais.\n\n"
            "¶30 Outro parágrafo.\n", encoding="utf-8")
        (eng / "enquadramento.md").write_text(C["ENQUADRAMENTO"], encoding="utf-8")
        self.assertEqual(sorted(P["transfer_units"](eng).values()),
                         ["process-question", "process-rule", "synopsis-label"])
        a = P["resolve_ref"](eng, "_capture/notas.docx.text.md#¶3")
        b = P["resolve_ref"](eng, "_capture/notas.docx.text.md#¶30")
        self.assertEqual((a["status"], b["status"]), ("ok", "ok"))
        self.assertNotEqual(a["digest"], b["digest"], "¶3 apanhou o ¶30")
        d = C["draft_v1"]()
        d["details"] = []
        d["nodes"][2]["evidence"].append({"ref": "_capture/notas.docx.text.md#¶3"})
        d, _ = P["stamp"](eng, d)
        (base / "d.json").write_text(json.dumps(d), encoding="utf-8")
        r = P["publish"](eng, d, base / "d.json")
        self.assertTrue(r["published"], r.get("verdict"))


class ExtraccaoIncompleta(Base):

    def test_a_failed_extraction_stays_visible_in_the_check_and_the_page(self):
        (self.eng / "_capture" / "precos.xlsx.extraction.json").write_text(json.dumps(
            {"artefact": "aisa.capture.extraction", "status": "failed",
             "reason": "ficheiro protegido por palavra-passe"}), encoding="utf-8")
        v = P["check"](self.eng, self.stamped())
        self.assertTrue(v["valid"], v["errors"])
        gaps = [g for g in v["gaps"] if g["code"] == "MAP-SOURCE-INCOMPLETE"]
        self.assertEqual(len(gaps), 1)
        self.assertIn("palavra-passe", gaps[0]["message"])
        self.published()
        html = P["render_html"](self.eng)
        self.assertIn("Leitura incompleta", html)
        self.assertIn("palavra-passe", html)


class LigacaoDasSkills(unittest.TestCase):

    def test_capture_authors_publishes_renders_and_asks_the_owner(self):
        for frase in ("5d. **Process map", "process-map.guide.md", "process_map.py stamp",
                      "process_map.py publish", "process_map.py render",
                      "5e. **Owner validation of the map**", "process_map.py questions",
                      "process_map.py approval-block", "Falta algum passo, saída ou quem a recebe?",
                      "never one question per cell"):
            self.assertIn(frase, CAPTURE)
        self.assertLess(CAPTURE.index("5. **L2 — process model**"), CAPTURE.index("5d. **Process map"))

    def test_round_reads_the_map_status_before_the_passagem(self):
        self.assertIn("2b. **Process map check**", ROUND)
        self.assertIn("process_map.py status --engagement <slug> --json", ROUND)
        self.assertLess(ROUND.index("2b. **Process map check**"),
                        ROUND.index("3. **Determine the passagem**"))

    def test_the_guide_exists_and_forbids_satisfying_the_validator(self):
        g = GUIDE.read_text(encoding="utf-8")
        self.assertIn("Nunca** se\n  apaga uma dúvida", g)
        self.assertIn("nunca filtram", g)


if __name__ == "__main__":
    unittest.main()
