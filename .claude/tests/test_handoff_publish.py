# -*- coding: utf-8 -*-
"""handoff-v1 F2 — rascunho e publicação das autoridades pelo coordenador (DESENHO §3).

    T17  edição directa da SU com grafo divergente -> edição preservada, publicação
         inconsistente bloqueada, reconciliação explícita
    T13  publicar o mesmo rascunho outra vez -> o mesmo recibo, sem duplicar
    T11  base ou input do rascunho mudou -> STALE_INPUT, rascunho intacto

e as regras de integridade que o caminho coordenado partilha com o guarda
(`workflow.su_problems`, `workflow.state_problems`).

Stdlib apenas. Engagement sintético (`test_migration.make`).
"""
import json
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
FIX = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_migration.py"))
M = runpy.run_path(str(TOOLS / "migrate.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))
B = runpy.run_path(str(TOOLS / "bootstrap.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
G = runpy.run_path(str(TOOLS / "graph.py"))

SU = "shared-understanding.md"
ANCORA = "| C-001 | data | Base partilhada | inicial | 2026-01-01 | organizacional | R-01 |"
NOVA = ("| C-050 | business | Linha nova | answers.md#U-001 | 2026-03-01 | organizacional "
        "| R-02 |")


def engagement(tmp):
    projects = Path(tmp) / "projects"
    projects.mkdir()
    eng = Path(FIX["make"](str(projects), FIX["NOVO"]))
    M["apply"](eng)
    assert B["bootstrap"](eng)["ready"], "a premissa do caso caiu"
    return eng


def copia(d, rel=SU):
    return Path(d["path"]) / rel


def acrescenta(d, linha=NOVA):
    c = copia(d)
    c.write_text(c.read_text(encoding="utf-8").replace(ANCORA, ANCORA + "\n" + linha, 1),
                 encoding="utf-8", newline="\n")


def recibos(eng):
    return sorted(p.name for p in (eng / "_ops" / "receipts").glob("*.json"))


class Publicacao(unittest.TestCase):

    def test_su_and_mirror_are_one_operation_with_one_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            antes = recibos(eng)
            d = R["draft"](eng, [SU], reads=["answers.md"])
            acrescenta(d)
            r = R["publish"](eng, d["draft"])
            novos = [x for x in recibos(eng) if x not in antes]
            self.assertEqual(len(novos), 1, novos)
            self.assertTrue(novos[0].startswith("publish-"))
            rev = r["receipt"]["revision"]
            self.assertIn(SU, rev)
            self.assertTrue([k for k in rev if k.startswith("_graph/")],
                            "o espelho não foi na mesma operação")
            self.assertEqual(r["receipt"]["read_set"]["answers.md"],
                             O["digest"](eng / "answers.md"))
            self.assertIn("C-050", {n["id"] for n in G["read"](eng)["nodes"]})
            self.assertTrue(B["bootstrap"](eng)["ready"])

    def test_the_draft_is_not_an_authority_and_nobody_reads_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU])
            acrescenta(d)
            boot = B["bootstrap"](eng)
            self.assertTrue(boot["ready"], "um rascunho mudou a leitura da autoridade")
            self.assertNotIn("C-050", {r["id"] for r in boot["snapshot"]["rows"]})
            self.assertNotIn("C-050", (eng / SU).read_text(encoding="utf-8"))

    def test_other_files_publish_with_the_su(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU, "lens-outputs/business.md"])
            acrescenta(d)
            out = copia(d, "lens-outputs/business.md")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text("## R-02 — business\n", encoding="utf-8")
            r = R["publish"](eng, d["draft"])
            self.assertIn("lens-outputs/business.md", r["receipt"]["revision"])
            self.assertTrue((eng / "lens-outputs" / "business.md").is_file())


class T13_MesmoRascunho(unittest.TestCase):

    def test_publishing_the_same_draft_twice_is_the_same_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU])
            acrescenta(d)
            r1 = R["publish"](eng, d["draft"])
            n = recibos(eng)
            r2 = R["publish"](eng, d["draft"])
            self.assertTrue(r2["replayed"])
            self.assertEqual(r1["operation_id"], r2["operation_id"])
            self.assertEqual(recibos(eng), n, "a repetição criou outro recibo")
            self.assertEqual((eng / SU).read_text(encoding="utf-8").count("C-050"), 1,
                             "a linha foi duplicada")

    def test_an_unchanged_draft_publishes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            antes = recibos(eng)
            d = R["draft"](eng, [SU])
            r = R["publish"](eng, d["draft"])
            self.assertEqual(r["published"], [])
            self.assertEqual(recibos(eng), antes)


class T11_RascunhoDesactualizado(unittest.TestCase):

    def test_a_base_that_moved_is_stale_and_the_draft_survives(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU])
            acrescenta(d)
            # outra sessão publica entretanto
            d2 = R["draft"](eng, [SU])
            acrescenta(d2, NOVA.replace("C-050", "C-051"))
            R["publish"](eng, d2["draft"])
            conteudo = copia(d).read_bytes()
            with self.assertRaises(R["_O"]["OperationError"]) as ctx:
                R["publish"](eng, d["draft"])
            self.assertEqual(O["stable_code"](ctx.exception.code), "STALE_INPUT")
            self.assertEqual(copia(d).read_bytes(), conteudo, "o rascunho foi mexido")
            su = (eng / SU).read_text(encoding="utf-8")
            self.assertIn("C-051", su, "a publicação da outra sessão perdeu-se")
            self.assertNotIn("C-050", su, "last-writer-wins silencioso")

    def test_a_declared_read_that_moved_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU], reads=["answers.md"])
            acrescenta(d)
            (eng / "answers.md").write_text("# Respostas\n\n## U-001\n\n> outra\n",
                                            encoding="utf-8")
            with self.assertRaises(R["_O"]["OperationError"]) as ctx:
                R["publish"](eng, d["draft"])
            self.assertEqual(ctx.exception.code, "STALE_INPUT")
            self.assertEqual(ctx.exception.detail["path"], "answers.md")


class Integridade(unittest.TestCase):
    """O caminho coordenado não é mais largo do que o Edit: as mesmas regras."""

    def _recusa(self, eng, d, codigo):
        with self.assertRaises(R["ResolveError"]) as ctx:
            R["publish"](eng, d["draft"])
        self.assertEqual(ctx.exception.code, "INTEGRITY_FAILURE")
        self.assertIn(codigo, [p["source_code"] for p in ctx.exception.detail["problems"]])
        self.assertTrue(copia(d).exists() or (Path(d["path"]) / "_state.json").exists(),
                        "a recusa apagou o rascunho")

    def test_a_removed_su_row_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU])
            c = copia(d)
            c.write_text(c.read_text(encoding="utf-8").replace(ANCORA + "\n", "", 1),
                         encoding="utf-8")
            self._recusa(eng, d, "SU_ROW_REMOVED")

    def test_a_confirmed_row_without_locator_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU])
            acrescenta(d, NOVA.replace("answers.md#U-001", "as personas concordam"))
            self._recusa(eng, d, "CONFIRMED_WITHOUT_LOCATOR")

    def test_the_workflow_block_does_not_change_by_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, ["_state.json"])
            p = Path(d["path"]) / "_state.json"
            st = json.loads(p.read_text(encoding="utf-8"))
            st["workflow"]["route"] = "change-impact"
            p.write_text(json.dumps(st), encoding="utf-8")
            self._recusa(eng, d, "WORKFLOW_CHANGED")

    def test_state_keys_are_not_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, ["_state.json"])
            p = Path(d["path"]) / "_state.json"
            st = json.loads(p.read_text(encoding="utf-8"))
            st.pop("pack")
            p.write_text(json.dumps(st), encoding="utf-8")
            self._recusa(eng, d, "STATE_KEYS_DROPPED")

    def test_coordinated_state_and_escapes_are_not_draftable(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            for rel, codigo in (("_graph/graph.jsonl", "NOT_DRAFTABLE"),
                                ("_ops/pending.json", "NOT_DRAFTABLE"),
                                ("_work/checkpoint.json", "NOT_DRAFTABLE"),
                                ("../fora.md", "BAD_PATH"),
                                ("dashboard.html", "NOT_DRAFTABLE")):
                with self.subTest(rel=rel), self.assertRaises(R["ResolveError"]) as ctx:
                    R["draft"](eng, [rel])
                self.assertEqual(ctx.exception.code, codigo)

    def test_a_legacy_engagement_cannot_open_a_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            projects = Path(tmp) / "projects"
            projects.mkdir()
            eng = Path(FIX["make"](str(projects), FIX["NOVO"]))
            (eng / "_state.json").write_text(json.dumps({"pack": "pp"}), encoding="utf-8")
            # cada `runpy` tem a sua classe: a que o motor levanta e a do `_O` dele
            with self.assertRaises(R["_O"]["OperationError"]) as ctx:
                R["draft"](eng, [SU])
            self.assertEqual(ctx.exception.code, "UNSUPPORTED_PROFILE")
            self.assertFalse((eng / "_drafts").exists())

    def test_nothing_publishes_over_a_pending_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU])
            acrescenta(d)
            O["_atomic_write"](O["pending_path"](eng), json.dumps(
                {"intent_version": 1, "operation_id": "op-x", "request_hash": "h",
                 "owner": {}, "before": {}, "after": {"x.md": "f" * 64},
                 "staging": "_ops/staging/op-x"}))
            with self.assertRaises(R["ResolveError"]) as ctx:
                R["publish"](eng, d["draft"])
            self.assertEqual(ctx.exception.code, "NOT_READY")


class T17_EdicaoDirecta(unittest.TestCase):
    """Edit direto na SU com grafo divergente: preservar, bloquear, reconciliar à vista."""

    def test_direct_edit_preserved_publication_blocked_reconciliation_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            su = eng / SU
            su.write_text(su.read_text(encoding="utf-8").replace(
                ANCORA, ANCORA + "\n" + NOVA, 1), encoding="utf-8", newline="\n")
            editado = su.read_bytes()

            # bloquear: nenhuma publicação sobre o estado divergente
            d = R["draft"](eng, ["answers.md"])
            (Path(d["path"]) / "answers.md").write_text("# Respostas\n\nnova\n",
                                                        encoding="utf-8")
            with self.assertRaises(R["ResolveError"]) as ctx:
                R["publish"](eng, d["draft"])
            self.assertEqual(ctx.exception.code, "NOT_READY")
            codigos = [l["code"] for l in ctx.exception.detail["limitations"]]
            self.assertIn("AUTHORITY_UNMIRRORED", codigos)

            # preservar: a edição continua lá, byte a byte
            self.assertEqual(su.read_bytes(), editado)

            # reconciliar explicitamente: ver primeiro, publicar só com --apply
            plano = R["reconcile"](eng)
            self.assertEqual(plano["status"], "planned")
            self.assertIn("C-050", plano["new_rows"])
            self.assertFalse(B["bootstrap"](eng)["ready"])
            feito = R["reconcile"](eng, apply=True)
            self.assertEqual(feito["status"], "mirrored")
            self.assertTrue(feito["receipt"]["operation_id"].startswith("mirror-"))
            self.assertEqual(su.read_bytes(), editado)
            self.assertTrue(B["bootstrap"](eng)["ready"])

            # e a publicação que estava bloqueada passa sobre o estado reconciliado
            r = R["publish"](eng, d["draft"])
            self.assertIn("answers.md", r["published"])


class CLI(unittest.TestCase):

    def _run(self, *args):
        return subprocess.run([sys.executable, str(TOOLS / "resolve.py")] + list(args),
                              capture_output=True, text=True, timeout=300,
                              env=dict(os.environ, PYTHONIOENCODING="utf-8"))

    def test_draft_then_publish_from_the_command_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            p = self._run("draft", "--engagement", str(eng), "--files", SU, "--json")
            self.assertEqual(p.returncode, 0, p.stderr)
            d = json.loads(p.stdout)
            acrescenta(d)
            p = self._run("publish", "--engagement", str(eng), "--draft", d["draft"],
                          "--json")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn(SU, json.loads(p.stdout)["published"])

    def test_a_stale_publish_prints_the_stable_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU], reads=["answers.md"])
            acrescenta(d)
            (eng / "answers.md").write_text("# mudou\n", encoding="utf-8")
            p = self._run("publish", "--engagement", str(eng), "--draft", d["draft"])
            self.assertEqual(p.returncode, 1)
            env = json.loads(p.stderr)
            self.assertEqual(env["code"], "STALE_INPUT")
            self.assertEqual(env["reasons"][0]["source_code"], "STALE_INPUT")


if __name__ == "__main__":
    unittest.main()
