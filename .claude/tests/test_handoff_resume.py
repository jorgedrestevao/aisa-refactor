# -*- coding: utf-8 -*-
"""handoff-v1 F2.4 — retoma a frio (DESENHO §5; plan 04 §Retoma).

    T09  cold resume sem conversa anterior -> objectivo, autorizações, bloqueios e próximo
         trabalho correcto, reconstruídos do repositório
    T16  contexto necessário excede o orçamento -> estado parcial explícito e expansão;
         nenhum bloqueio crítico omitido em silêncio

A retoma corre num processo novo (a CLI), sobre um engagement deixado a meio por uma
«sessão» anterior que morreu: uma tarefa `running`, um resultado recebido e não integrado.
Só lê: os bytes de todas as autoridades e do checkpoint ficam iguais (F0 D02).

Stdlib apenas. Engagement sintético (`test_migration.make`).
"""
import hashlib
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
B = runpy.run_path(str(TOOLS / "bootstrap.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
W = R["_B"]["_W"]
O = R["_O"]

SU = "shared-understanding.md"
ANCORA = "| C-001 | data | Base partilhada | inicial | 2026-01-01 | organizacional | R-01 |"
NOVA = ("| C-050 | business | Linha nova | answers.md#U-001 | 2026-03-01 | organizacional "
        "| R-02 |")
PEDIDO = "Quero reduzir o tempo de fecho do preço semanal"


def engagement(tmp):
    projects = Path(tmp) / "projects"
    projects.mkdir()
    eng = Path(FIX["make"](str(projects), FIX["NOVO"]))
    (eng / "context.json").write_text(json.dumps({"engagement": "eng",
                                                  "literal_request": PEDIDO},
                                                 ensure_ascii=False), encoding="utf-8")
    M["apply"](eng)
    assert B["bootstrap"](eng)["ready"]
    return eng


def sessao_que_morreu(eng):
    """TASK-001: lente de negócio com resultado recebido e por integrar.
    TASK-002: lente de dados a correr quando a sessão morreu, sem resultado."""
    t1 = W["task_plan"](eng, "lens-business", ["linhas publicadas"], ["answers.md"])["task"]
    W["task_start"](eng, t1)
    d = R["draft"](eng, [SU], reads=["answers.md"], task=t1)
    c = Path(d["path"]) / SU
    c.write_text(c.read_text(encoding="utf-8").replace(ANCORA, ANCORA + "\n" + NOVA, 1),
                 encoding="utf-8", newline="\n")
    W["task_receive"](eng, t1, d["draft"])
    t2 = W["task_plan"](eng, "lens-data", ["linhas publicadas"], ["answers.md"])["task"]
    W["task_start"](eng, t2)
    return t1, t2, d["draft"]


def retoma(eng, *extra):
    p = subprocess.run([sys.executable, str(TOOLS / "workflow.py"), "resume",
                        "--engagement", str(eng), "--json"] + list(extra),
                       capture_output=True, text=True, timeout=300,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return p.returncode, json.loads(p.stdout)


def bytes_de(eng):
    return {p.relative_to(eng).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in eng.rglob("*") if p.is_file() and "_ops" not in p.parts}


class T09_RetomaAFrio(unittest.TestCase):

    def test_a_fresh_process_rebuilds_objective_authorizations_blockers_and_next_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t1, t2, rascunho = sessao_que_morreu(eng)
            rc, out = retoma(eng)
            self.assertEqual(rc, 0, out)
            self.assertTrue(out["ok"])
            self.assertEqual(out["objective"]["text"], PEDIDO)
            self.assertEqual(out["objective"]["ref"], "context.json#literal_request")
            self.assertEqual([a["id"] for a in out["authorizations"]], ["D-001", "D-002"])
            self.assertIn("U-001", [b["id"] for b in out["blockers"]],
                          "o bloqueio crítico aberto não foi reconstruído")
            self.assertEqual(out["tasks"], {"running": [t1, t2]})
            self.assertEqual({(p["task"], p["to"]) for p in out["reconcile_proposal"]},
                             {(t1, "blocked"), (t2, "planned")})
            self.assertEqual([r["result"] for r in out["results_pending"]], ["RES-001"])
            self.assertEqual(out["results_pending"][0]["freshness_now"], "current")
            self.assertIn("task reconcile", out["next_action"]["action"],
                          "a próxima acção não reconcilia antes de relançar")

    def test_the_next_work_follows_the_state_after_each_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t1, t2, rascunho = sessao_que_morreu(eng)
            W["tasks_reconcile"](eng)
            _rc, out = retoma(eng)
            self.assertEqual(out["reconcile_proposal"], [])
            self.assertIn("resolve.py publish", out["next_action"]["action"])
            self.assertIn(rascunho, out["next_action"]["action"])
            R["publish"](eng, rascunho)
            _rc, out = retoma(eng)
            self.assertEqual(out["results_pending"], [])
            self.assertIn("task start {}".format(t2), out["next_action"]["action"])

    def test_a_stale_received_result_is_not_offered_for_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t1, _t2, _d = sessao_que_morreu(eng)
            W["tasks_reconcile"](eng)
            (eng / "answers.md").write_text("# Respostas\n\n## U-001\n\n> mudou\n",
                                            encoding="utf-8")
            _rc, out = retoma(eng)
            self.assertEqual(out["results_pending"][0]["freshness_now"], "stale")
            self.assertNotIn("publish", out["next_action"]["action"])
            self.assertIn(t1, out["next_action"]["action"])

    def test_resume_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            sessao_que_morreu(eng)
            antes = bytes_de(eng)
            retoma(eng)
            self.assertEqual(bytes_de(eng), antes)

    def test_a_pending_operation_is_recovery_required_before_anything(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            O["_atomic_write"](O["pending_path"](eng), json.dumps(
                {"intent_version": 1, "operation_id": "op-x", "request_hash": "h",
                 "owner": {}, "before": {}, "after": {"x.md": "f" * 64},
                 "staging": "_ops/staging/op-x"}))
            rc, out = retoma(eng)
            self.assertEqual(rc, 1)
            self.assertEqual(out["code"], "RECOVERY_REQUIRED")
            self.assertIn("recover", out["next_action"]["action"])
            self.assertEqual(out["tasks"], {}, "leu o checkpoint sobre uma pendência")

    def test_a_legacy_engagement_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            projects = Path(tmp) / "projects"
            projects.mkdir()
            eng = Path(FIX["make"](str(projects), FIX["NOVO"]))
            (eng / "_state.json").write_text(json.dumps({"pack": "pp"}), encoding="utf-8")
            rc, out = retoma(eng)
            self.assertEqual(rc, 1)
            self.assertEqual(out["code"], "UNSUPPORTED_PROFILE")

    def test_an_undeclared_objective_is_said_not_invented(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            (eng / "context.json").unlink()
            _rc, out = retoma(eng)
            self.assertIsNone(out["objective"]["text"])
            self.assertIn("OBJECTIVE_UNDECLARED", [l["code"] for l in out["limitations"]])


class T16_OrcamentoExcedido(unittest.TestCase):

    def test_over_budget_is_partial_named_and_never_drops_a_critical_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            rc, out = retoma(eng, "--budget", "0")
            self.assertEqual(rc, 0, out)
            ctx = out["context"]
            self.assertFalse(ctx["complete"])
            self.assertIn("U-001", ctx["omitted_critical"])
            self.assertIn("U-001", [b["id"] for b in out["blockers"]],
                          "um crítico fora do orçamento desapareceu da retoma")
            b = next(b for b in out["blockers"] if b["id"] == "U-001")
            self.assertIsNone(b["text"], "inventou texto para o que não coube")
            self.assertIn("--budget", ctx["expand"]["action"])
            self.assertIn("PARCIAL", ctx["expand"]["reason"])

    def test_within_budget_is_complete_and_carries_the_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            _rc, out = retoma(eng)
            self.assertTrue(out["context"]["complete"])
            self.assertNotIn("expand", out["context"])
            b = next(b for b in out["blockers"] if b["id"] == "U-001")
            self.assertTrue(b["text"])


if __name__ == "__main__":
    unittest.main()
