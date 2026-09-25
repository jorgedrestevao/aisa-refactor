"""process-map M2 — a validação do mapa pelo dono e as perguntas agrupadas.

Casos (docs/process-map/PLANO.md §15): MAP-15 (validação com hash antigo, forjada ou com
campos em falta não é validação actual), MAP-16 (o dono valida a estrutura com uma hipótese
aberta: a marca e a dúvida ficam), a correcção pelo dono (nova versão → a validação antiga
não transita), e o bloco gerado pelo motor (validador humano, âmbito, condições, data).

    python .claude/tests/test_process_map_validation.py
"""
import json
import os
import runpy
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_process_map_core.py"), run_name="helpers")
P = C["P"]
OWNER = "owner (Responsável de Pricing, via AskUserQuestion)"


class Base(C["Base"]):

    def setUp(self):
        super().setUp()
        self.draft = self.stamped()
        r = self.publish(self.draft)
        self.assertTrue(r["published"], r)

    def append_decision(self, text):
        p = self.eng / "decisions.md"
        p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")

    def validate(self, scope="processo diário de preço", conditions="MAPG-001 por esclarecer",
                 ts="2026-09-25T10:00:00Z"):
        self.append_decision(P["approval_block"](self.eng, scope, conditions, OWNER, ts))

    def v2(self, change):
        d = C["draft_v1"]()
        d["base"] = P["load"](self.eng)["digest"]
        change(d)
        d = self.stamped(d)
        r = self.publish(d)
        self.assertTrue(r["published"], r.get("verdict"))
        return r


class Bloco(Base):

    def test_the_motor_writes_the_digest_of_the_published_version(self):
        text = P["approval_block"](self.eng, "processo diário", "nenhuma", OWNER,
                                   "2026-09-25T10:00:00Z")
        self.assertIn("## D-002 — Mapa do processo mp-v01 validado", text)
        self.assertIn(P["load"](self.eng)["digest"], text)

    def test_a_non_human_validator_is_refused(self):
        for who in ("executor", "owner (claude, via AskUserQuestion)", "owner (Pedro)"):
            with self.subTest(who):
                with self.assertRaises(ValueError):
                    P["approval_block"](self.eng, "x", "nenhuma", who, "2026-09-25T10:00:00Z")

    def test_scope_and_conditions_are_mandatory(self):
        with self.assertRaises(ValueError):
            P["approval_block"](self.eng, " ", "nenhuma", OWNER, "2026-09-25T10:00:00Z")
        with self.assertRaises(ValueError):
            P["approval_block"](self.eng, "x", "", OWNER, "2026-09-25T10:00:00Z")

    def test_a_block_cannot_predate_a_registered_decision(self):
        with self.assertRaises(ValueError):
            P["approval_block"](self.eng, "x", "nenhuma", OWNER, "2025-01-01T00:00:00Z")

    def test_without_a_map_there_is_nothing_to_validate(self):
        (self.eng / "_map" / "map.json").unlink()
        with self.assertRaises(ValueError):
            P["approval_block"](self.eng, "x", "nenhuma", OWNER, "2026-09-25T10:00:00Z")


class Leitura(Base):

    def test_no_block_reads_not_validated(self):
        self.assertEqual(P["validation"](self.eng)["status"], "not_validated")

    def test_a_complete_block_for_these_bytes_reads_validated(self):
        self.validate()
        v = P["validation"](self.eng)
        self.assertEqual((v["status"], v["version"], v["decision"]), ("validated", "mp-v01",
                                                                      "D-002"))
        self.assertEqual(v["conditions"], "MAPG-001 por esclarecer")

    def test_validating_never_touches_the_map(self):
        before = (self.eng / "_map" / "map.json").read_bytes()
        self.validate()
        self.assertEqual((self.eng / "_map" / "map.json").read_bytes(), before)


class MAP15_ValidacaoNaoAplicavel(Base):

    def test_a_validation_of_an_older_version_is_stale(self):
        self.validate()
        self.v2(lambda d: d["nodes"][1].__setitem__("label", "Calcula o preço de referência"))
        v = P["validation"](self.eng)
        self.assertEqual(v["status"], "stale")
        self.assertIn("mp-v01", v["detail"])
        self.assertIn("mp-v02", v["detail"])

    def test_a_forged_digest_is_invalid(self):
        text = P["approval_block"](self.eng, "x", "nenhuma", OWNER, "2026-09-25T10:00:00Z")
        text = text.replace(P["load"](self.eng)["digest"], "a" * 64)
        self.append_decision(text)
        v = P["validation"](self.eng)
        self.assertEqual(v["status"], "invalid")
        self.assertIn("digest", v["detail"])

    def test_a_block_with_missing_fields_or_a_non_human_is_invalid(self):
        good = P["approval_block"](self.eng, "x", "nenhuma", OWNER, "2026-09-25T10:00:00Z")
        for label, bad in (
                ("sem âmbito", "\n".join(l for l in good.splitlines()
                                         if not l.startswith("- **Scope**")) + "\n"),
                ("executor", good.replace(OWNER, "executor [ÂMBITO AUTORIZADO]")),
                ("data", good.replace("2026-09-25T10:00:00Z", "ontem"))):
            with self.subTest(label):
                (self.eng / "decisions.md").write_text(C["DECISIONS"] + bad, encoding="utf-8")
                self.assertEqual(P["validation"](self.eng)["status"], "invalid")

    def test_a_title_alone_is_not_a_validation(self):
        self.append_decision("\n## D-002 — Mapa do processo mp-v01 validado\n")
        self.assertEqual(P["validation"](self.eng)["status"], "invalid")


class MAP16_HipoteseAberta(Base):

    def test_the_owner_validates_the_structure_and_the_doubt_stays(self):
        self.v2(lambda d: d["nodes"][2].__setitem__("marker", "HYPOTHESIS"))
        self.validate(conditions="MAPG-001 e a hipótese sobre o resumo diário ficam por fechar")
        self.assertEqual(P["validation"](self.eng)["status"], "validated")
        m = P["load"](self.eng)["map"]
        self.assertEqual(m["nodes"][2]["marker"], "HYPOTHESIS",
                         "a validação promoveu uma hipótese")
        ids = [i["id"] for g in P["questions"](self.eng) for i in g["items"]]
        self.assertIn("MAPG-001", ids, "a dúvida desapareceu com a validação")
        html = P["render_html"](self.eng)
        self.assertIn("validado pelo dono", html)
        self.assertIn("Quem consome o resumo ao fim de semana?", html)
        self.assertIn("hipótese", html)


class CorrecaoPeloDono(Base):

    def test_a_correction_is_a_new_version_and_needs_its_own_validation(self):
        self.validate()

        def add_step(d):
            d["nodes"].append({"id": "MAPN-004", "kind": "step", "label": "Envia aos comerciais",
                               "lane": "MAPL-001", "order": 3, "marker": "OBSERVED",
                               "evidence": [{"ref": "enquadramento.md#T4"}]})
            d["edges"].append({"id": "MAPE-003", "src": "MAPN-003", "dst": "MAPN-004",
                               "kind": "normal", "marker": "OBSERVED",
                               "evidence": [{"ref": "enquadramento.md#T4"}]})
        r = self.v2(add_step)
        self.assertEqual(r["version"], "mp-v02")
        self.assertEqual(P["validation"](self.eng)["status"], "stale")
        self.validate(ts="2026-09-25T11:00:00Z")
        v = P["validation"](self.eng)
        self.assertEqual((v["status"], v["version"], v["decision"]), ("validated", "mp-v02",
                                                                      "D-003"))
        v1 = json.loads((self.eng / "_map" / "history" / "mp-v01.json").read_text("utf-8"))
        self.assertNotIn("MAPN-004", {n["id"] for n in v1["nodes"]})


class PerguntasAgrupadas(Base):

    def test_doubts_are_grouped_by_theme_structure_first(self):
        def more(d):
            d["nodes"].append({"id": "MAPN-004", "kind": "exception", "label": "Ficheiro corrompe",
                               "lane": "MAPL-001", "order": 1, "marker": "UNKNOWN",
                               "evidence": []})
            d["gaps"] += [
                {"id": "MAPG-002", "attaches_to": ["MAPN-004"],
                 "question": "Quantas vezes por mês corrompe?"},
                {"id": "MAPG-003", "attaches_to": ["GLOBAL"],
                 "question": "Há um plano B se o preço não sair até às 10:00?"},
                {"id": "MAPG-004", "attaches_to": ["MAPD-001"],
                 "question": "Que indicador define o spread?"}]
        self.v2(more)
        qs = P["questions"](self.eng)
        self.assertEqual([g["group"] for g in qs], ["estrutura", "saidas", "excecoes", "ambito"])
        where = {i["id"]: g["group"] for g in qs for i in g["items"]}
        self.assertEqual(where, {"MAPG-001": "saidas", "MAPG-002": "excecoes",
                                 "MAPG-003": "ambito", "MAPG-004": "estrutura"})
        self.assertTrue(all(g["validates"] for g in qs if g["group"] != "excecoes"))

    def test_an_open_orphan_is_asked_an_exclusion_is_not(self):
        def orphans(d):
            d["details"] = d["details"][:1]
            d["retired_ids"] = [{"id": "MAPD-002", "reason": "o cálculo de 2024 sai do passo "
                                                            "até se saber se ainda se usa"}]
            d["orphans"] = [{"ref": "_capture/precos-2024.xlsx.calc-chain.json#CALC-001",
                             "reason": "undetermined", "materiality": "undetermined",
                             "note": "o cálculo de 2024 ainda se usa?"}]
        self.v2(orphans)
        items = [i["question"] for g in P["questions"](self.eng) for i in g["items"]]
        self.assertIn("o cálculo de 2024 ainda se usa?", items)


class CLI(Base):

    def run_cli(self, *args):
        env = dict(os.environ, AISA_ENGAGEMENTS_ROOT=str(self.base), PYTHONIOENCODING="utf-8")
        return subprocess.run([sys.executable, "-B", str(C["MOTOR"]), *args],
                              capture_output=True, text=True, encoding="utf-8", env=env)

    def test_status_reports_the_validation(self):
        r = self.run_cli("status", "--engagement", "novo", "--json")
        self.assertEqual(json.loads(r.stdout)["validation"]["status"], "not_validated")
        self.validate()
        r = self.run_cli("status", "--engagement", "novo", "--json")
        self.assertEqual(json.loads(r.stdout)["validation"]["status"], "validated")

    def test_approval_block_refuses_a_non_human_with_exit_two(self):
        r = self.run_cli("approval-block", "--engagement", "novo", "--scope", "x",
                         "--conditions", "nenhuma", "--validated-by", "executor")
        self.assertEqual(r.returncode, 2)
        r = self.run_cli("approval-block", "--engagement", "novo", "--scope", "x",
                         "--conditions", "nenhuma", "--validated-by", OWNER,
                         "--timestamp", "2026-09-25T10:00:00Z", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Mapa do processo mp-v01 validado", json.loads(r.stdout)["block"])


if __name__ == "__main__":
    unittest.main()
