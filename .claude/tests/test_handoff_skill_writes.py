# -*- coding: utf-8 -*-
"""handoff-v1 F2.5 — as skills escrevem as autoridades pelo coordenador.

Desenho: `docs/handoff-v1/F2/DESENHO.md` §3 (Q1, Q2). Protocolo único:
`library/kernel/orchestration.md` → *Writing an authority*.

Contrato textual, com o limite declarado: estes testes lêem instruções, não observam uma
sessão. Provam que nenhuma skill manda escrever uma autoridade no sítio, que todos os
escritores apontam o protocolo, e que o que as skills mandam correr existe no motor. O
comportamento do motor está nos testes de `resolve.draft`/`publish`
(`test_handoff_publish.py`) e no nascimento (`test_graph_birth.W8d`).

Também: a regra da linha de decisão (`D-NNN` cita `decisions.md#D-NNN`, com o bloco
presente) e o `capture_run` derivado do log (a captura não escreve `_state.json`).
"""
import json
import re
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
D = runpy.run_path(str(TOOLS / "dashboard.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))

INSTRUCOES = (sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
              + sorted((ROOT / ".claude" / "agents").glob("*.md"))
              + sorted((ROOT / ".claude" / "commands").glob("*.md")))

# Os escritores das seis autoridades (Q2). Cada um aponta o protocolo.
ESCRITORES = ("aisa-start", "aisa-round", "aisa-frame", "aisa-options", "aisa-decide",
              "aisa-answer", "aisa-blueprint", "chairman-synthesis", "lens-technology")
PROTOCOLO = "Writing an authority"

# Instruções de escrita no sítio que o F2 retirou. Uma proibição («never `mv` a `.tmp`»)
# não conta: o padrão é o da instrução, não o da palavra.
NO_SITIO = (re.compile(r"Move-Item\s+-Force"),
            re.compile(r"_state\.json\.tmp`?\s*(?:→|->|, then rename)"),
            re.compile(r"(?i)write atomically"),
            re.compile(r"(?i)atomically:\s*tmp"),
            re.compile(r"(?i)one atomic write \(tmp"),
            re.compile(r"\((?:atomic)\)"))


def texto(p):
    return p.read_text(encoding="utf-8")


class NenhumaEscritaNoSitio(unittest.TestCase):

    def test_no_skill_tells_to_rename_a_tmp_over_an_authority(self):
        falhas = []
        for p in INSTRUCOES:
            t = texto(p)
            for rx in NO_SITIO:
                for m in rx.finditer(t):
                    falhas.append("{}: {!r}".format(p.relative_to(ROOT), m.group(0)))
        self.assertEqual(falhas, [])

    def test_every_authority_writer_points_to_the_protocol(self):
        falta = [s for s in ESCRITORES
                 if PROTOCOLO not in texto(ROOT / ".claude" / "skills" / s / "SKILL.md")]
        self.assertEqual(falta, [], "escritores sem o protocolo único")

    def test_the_chairman_agent_writes_the_draft_copy_and_never_publishes(self):
        t = texto(ROOT / ".claude" / "agents" / "chairman.md")
        self.assertIn("draft copy", t)
        self.assertIn("never open or publish a draft", t)

    def test_the_protocol_lives_in_the_kernel_once(self):
        orq = texto(ROOT / "library" / "kernel" / "orchestration.md")
        self.assertEqual(orq.count("## Writing an authority"), 1)
        for codigo in ("STALE_INPUT", "INTEGRITY_FAILURE", "NOT_READY", "CONCURRENT_WRITE"):
            self.assertIn(codigo, orq)

    def test_the_commands_the_skills_name_exist_in_the_engine(self):
        """O que as skills mandam correr tem de existir: `resolve.py draft|publish|
        reconcile` e `--op revalidate`."""
        nomes = set()
        for p in INSTRUCOES:
            nomes |= set(re.findall(r"resolve\.py (draft|publish|reconcile)\b", texto(p)))
        self.assertTrue({"draft", "publish"} <= nomes)
        for n in nomes:
            self.assertIn(n, ("draft", "publish", "reconcile"))
            self.assertTrue(callable(R[n]), n)
        self.assertIn("--op revalidate",
                      texto(ROOT / ".claude" / "skills" / "aisa-answer" / "SKILL.md"))

    def test_capture_writes_no_authority(self):
        t = texto(ROOT / ".claude" / "skills" / "aisa-capture" / "SKILL.md")
        self.assertNotIn("Increment `capture_run` in `_state.json`", t)
        self.assertIn("`_state.json` is **not** written", t)


class LinhaDeDecisao(unittest.TestCase):
    """states.md → *Confirmed threshold*, a regra do registo de decisão (2026-09-23)."""

    def linha(self, rid, evid):
        return {"id": rid, "state": "Confirmed", "resolved": False, "support": evid,
                "extra": "", "lens": "chair", "ronda": "D-01"}

    def test_a_decision_row_resolves_to_its_own_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp)
            (eng / "decisions.md").write_text("# Decisions\n\n## D-001 — Frame agreed\n",
                                              encoding="utf-8")
            a = D["audit_confirmed_locators"]([self.linha("D-001", "decisions.md#D-001")],
                                              eng)
            self.assertEqual(a["ids"], [])
            a = D["audit_confirmed_locators"]([self.linha("D-002", "decisions.md#D-002")],
                                              eng)
            self.assertEqual(a["ids"], ["D-002"], "bloco inexistente passou")

    def test_the_block_published_in_the_same_operation_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = D["audit_confirmed_locators"](
                [self.linha("D-003", "decisions.md#D-003")], Path(tmp),
                overlay={"decisions.md": "## D-003 — Adopt O-002\n"})
            self.assertEqual(a["ids"], [])

    def test_a_fact_never_confirms_itself_by_citing_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp)
            (eng / "decisions.md").write_text("## D-001 — x\n", encoding="utf-8")
            a = D["audit_confirmed_locators"]([self.linha("C-009", "decisions.md#D-001")],
                                              eng)
            self.assertEqual(a["ids"], ["C-009"])

    def test_a_decision_row_needs_its_own_record_not_another(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp)
            (eng / "decisions.md").write_text("## D-001 — x\n## D-004 — y\n",
                                              encoding="utf-8")
            a = D["audit_confirmed_locators"]([self.linha("D-004", "decisions.md#D-001")],
                                              eng)
            self.assertEqual(a["ids"], ["D-004"])

    def test_an_authorized_scope_row_cites_an_approval(self):
        """states.md regra 3 (Q6): `[ÂMBITO AUTORIZADO]` + `decisions.md#D-NNN` de uma
        aprovação (frame, solução, desenho) — e só com a marca."""
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp)
            (eng / "decisions.md").write_text(
                "# Decisions\n\n## D-001 — Frame agreed (F-01)\n\nx\n\n"
                "## D-002 — Nota interna\n\ny\n", encoding="utf-8")

            def c(rid, claim, evid):
                return dict(self.linha(rid, evid), claim=claim)
            rows = [c("C-010", "[ÂMBITO AUTORIZADO] o âmbito é só a loja", "decisions.md#D-001"),
                    c("C-011", "[ÂMBITO AUTORIZADO] x", "decisions.md#D-002"),
                    c("C-012", "[ÂMBITO AUTORIZADO] y", "decisions.md#D-009"),
                    c("C-013", "sem marca", "decisions.md#D-001")]
            a = D["audit_confirmed_locators"](rows, eng)
            self.assertEqual(sorted(a["ids"]), ["C-011", "C-012", "C-013"])
            self.assertEqual(a["com_locator"], 1)

    def test_the_decide_template_has_the_seven_confirmed_cells(self):
        """D09: a linha tinha 5 células numa tabela de 7."""
        t = texto(ROOT / ".claude" / "skills" / "aisa-decide" / "SKILL.md")
        linha = next(l for l in t.splitlines() if l.startswith("| D-NNN |"))
        self.assertEqual(linha.count("|") - 1, 7, linha)


class CaptureRun(unittest.TestCase):

    def test_the_run_count_is_derived_from_the_capture_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = Path(tmp)
            self.assertEqual(D["capture_run"](eng, {}), 0)
            (eng / "_capture").mkdir()
            (eng / "_capture" / "_capture-log.md").write_text(
                "L1 | a.xlsx | ok\nL2 | generated | run 1 | files: a.xlsx\n"
                "LT | b.docx | ok\nL2 | generated | run 2 | files: a.xlsx\n",
                encoding="utf-8")
            self.assertEqual(D["capture_run"](eng, {}), 2)
            self.assertEqual(D["capture_run"](eng, {"capture_run": 5}), 5,
                             "o valor antigo em _state.json deixou de contar como piso")


if __name__ == "__main__":
    unittest.main()
