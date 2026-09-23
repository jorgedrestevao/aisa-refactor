# -*- coding: utf-8 -*-
"""handoff-v1 F2.3 — checkpoint do trabalho, tarefas e resultados (DESENHO §4).

    T10  o rascunho cita um input que não declarou -> INCOMPLETE_READ_SET, não publicável
    T15  resultado recebido e não integrado -> não conta para prontidão; aparece na retoma
    T12  falha no limite da publicação com checkpoint -> revisão velha/nova ou recuperação
    T13  integração repetida -> idempotente, sem duplicar
    e: integração = autoridades + checkpoint numa operação; input da tarefa mudou desde o
    início -> STALE_INPUT; reconciliação depois de uma falha nunca relança nem promove.

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
B = runpy.run_path(str(TOOLS / "bootstrap.py"))
R = runpy.run_path(str(TOOLS / "resolve.py"))
W = R["_B"]["_W"]            # o workflow que o resolve usa — a mesma classe de erro
O = R["_O"]

SU = "shared-understanding.md"
CP = "_work/checkpoint.json"
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


def lente(eng, linha=NOVA, reads=("answers.md",), inputs=("answers.md",)):
    """O que o `/round` faz por lente: tarefa, rascunho com a tarefa, linha na cópia."""
    t = W["task_plan"](eng, "lens-business", ["linhas publicadas para R-02"], inputs)["task"]
    W["task_start"](eng, t)
    d = R["draft"](eng, [SU], reads=list(reads), task=t)
    c = Path(d["path"]) / SU
    c.write_text(c.read_text(encoding="utf-8").replace(ANCORA, ANCORA + "\n" + linha, 1),
                 encoding="utf-8", newline="\n")
    return t, d


def cp(eng):
    return json.loads((eng / CP).read_text(encoding="utf-8"))


def tarefa(eng, tid):
    return next(t for t in cp(eng)["tasks"] if t["id"] == tid)


class Integracao(unittest.TestCase):

    def test_authorities_and_checkpoint_are_one_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t, d = lente(eng)
            r = R["publish"](eng, d["draft"])
            rev = r["receipt"]["revision"]
            self.assertIn(SU, rev)
            self.assertIn(CP, rev, "o checkpoint não foi na mesma operação")
            self.assertEqual(tarefa(eng, t)["state"], "completed")
            res = [x for x in cp(eng)["results"] if x["task_id"] == t]
            self.assertEqual([x["status"] for x in res], ["integrated"])
            self.assertEqual(cp(eng)["last_integrated_operation"], r["operation_id"])
            self.assertTrue(B["bootstrap"](eng)["ready"])

    def test_the_checkpoint_holds_references_not_copies(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t, d = lente(eng)
            R["publish"](eng, d["draft"])
            texto = (eng / CP).read_text(encoding="utf-8")
            self.assertNotIn("Linha nova", texto, "o checkpoint copiou conteúdo da SU")
            self.assertNotIn("Base partilhada", texto)
            c = cp(eng)
            self.assertEqual(c["objective"], "context.json#literal_request")
            erros, _u = W["validate"](c, W["load_schema"]("handoff-work"))
            self.assertEqual(erros, [])

    def test_publishing_the_same_task_draft_twice_integrates_once(self):
        """T13 — repetir depois do sucesso não duplica resultado nem revisão."""
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t, d = lente(eng)
            r1 = R["publish"](eng, d["draft"])
            antes = cp(eng)
            r2 = R["publish"](eng, d["draft"])
            self.assertTrue(r2["replayed"])
            self.assertEqual(r1["operation_id"], r2["operation_id"])
            self.assertEqual(cp(eng), antes, "a repetição mexeu no checkpoint")

    def test_task_ids_are_never_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            a = W["task_plan"](eng, "x", ["c"])["task"]
            b = W["task_plan"](eng, "y", ["c"])["task"]
            self.assertEqual((a, b), ("TASK-001", "TASK-002"))
            self.assertEqual(cp(eng)["revision"], 2)


class T11_InputDaTarefaMudou(unittest.TestCase):

    def test_an_input_changed_since_start_is_stale_and_nothing_integrates(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t, d = lente(eng)
            (eng / "answers.md").write_text("# Respostas\n\n## U-001\n\n> mudou\n",
                                            encoding="utf-8")
            with self.assertRaises(O["OperationError"]) as ctx:
                R["publish"](eng, d["draft"])
            self.assertEqual(O["stable_code"](ctx.exception.code), "STALE_INPUT")
            self.assertEqual(tarefa(eng, t)["state"], "running")
            self.assertNotIn("C-050", (eng / SU).read_text(encoding="utf-8"))
            self.assertTrue((Path(d["path"]) / SU).exists(), "o rascunho perdeu-se")


class T10_ReadSetIncompleto(unittest.TestCase):

    def test_a_cited_input_that_was_not_declared_is_not_publishable(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            (eng / "frame.md").write_text("# frame\n", encoding="utf-8")
            t, d = lente(eng, linha=NOVA.replace("answers.md#U-001",
                                                 "answers.md#U-001; ver frame.md"))
            with self.assertRaises(R["ResolveError"]) as ctx:
                R["publish"](eng, d["draft"])
            self.assertEqual(ctx.exception.code, "INCOMPLETE_READ_SET")
            self.assertIn("frame.md", ctx.exception.detail["missing"])
            with self.assertRaises(W["WorkflowError"]) as ctx2:
                W["task_receive"](eng, t, d["draft"])
            self.assertEqual(ctx2.exception.code, "INCOMPLETE_READ_SET")
            self.assertEqual(tarefa(eng, t)["state"], "running")

    def test_ids_map_to_their_source_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            got = R["cited_sources"](eng, "cita D-003, TW-2, O-001, M-1, PM-U-004 e U-012")
            self.assertEqual(set(got), {"decisions.md", "options.md", "enquadramento.md",
                                        "_capture/process-model.md", SU})
            self.assertNotIn("U-004", got.get(SU, []), "PM-U-004 lido como linha da SU")

    def test_only_added_lines_are_checked(self):
        """A SU inteira cita o que outros leram; só o que o rascunho acrescenta conta."""
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            d = R["draft"](eng, [SU])
            gaps = R["read_set_gaps"](eng, R["read_draft"](eng, d["draft"]),
                                      {SU: (eng / SU).read_text(encoding="utf-8")})
            self.assertEqual(gaps, {})


class T15_RecebidoNaoIntegrado(unittest.TestCase):

    def test_a_received_result_does_not_count_and_shows_in_the_next_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t, d = lente(eng)
            out = W["task_receive"](eng, t, d["draft"])
            self.assertEqual(out["freshness"], "current")
            boot = B["bootstrap"](eng)
            self.assertTrue(boot["ready"])
            self.assertNotIn("C-050", {r["id"] for r in boot["snapshot"]["rows"]},
                             "um resultado recebido entrou na leitura da autoridade")
            self.assertNotIn("C-050", {n["id"] for n in
                                       R["_G"]["read"](eng)["nodes"]})
            c = cp(eng)
            self.assertEqual([r["status"] for r in c["results"]], ["received"])
            self.assertTrue([a for a in c["next_actions"] if d["draft"] in a["action"]],
                            c["next_actions"])
            # e integra depois, na mesma operação que a SU
            R["publish"](eng, d["draft"])
            self.assertEqual([r["status"] for r in cp(eng)["results"]], ["integrated"])

    def test_a_late_result_is_received_stale_never_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t, d = lente(eng)
            (eng / "answers.md").write_text("# Respostas\n\n## U-001\n\n> outra\n",
                                            encoding="utf-8")
            out = W["task_receive"](eng, t, d["draft"])
            self.assertEqual(out["freshness"], "stale")
            r = cp(eng)["results"][0]
            self.assertIn("answers.md", r["reason_not_integrated"])

    def test_receiving_the_same_draft_twice_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t, d = lente(eng)
            W["task_receive"](eng, t, d["draft"])
            antes = cp(eng)
            out = W["task_receive"](eng, t, d["draft"])
            self.assertTrue(out["replayed"])
            self.assertEqual(cp(eng), antes)


class Reconciliacao(unittest.TestCase):
    """Depois de uma falha, `running` não quer dizer que continua a correr."""

    def test_running_without_result_goes_back_to_planned(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t = W["task_plan"](eng, "lens-data", ["c"], ["answers.md"])["task"]
            W["task_start"](eng, t)
            out = W["tasks_reconcile"](eng)
            self.assertEqual(out["changed"], [{"task": t, "state": "planned"}])
            self.assertNotIn("sha256", tarefa(eng, t)["input_refs"][0])
            self.assertIsNone(cp(eng)["active_task"])

    def test_running_with_a_received_result_is_blocked_awaiting_integration(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t, d = lente(eng)
            W["task_receive"](eng, t, d["draft"])
            W["tasks_reconcile"](eng)
            x = tarefa(eng, t)
            self.assertEqual(x["state"], "blocked")
            self.assertTrue(x["blocker_refs"][0].endswith(":por-integrar"))
            self.assertEqual(cp(eng)["results"][0]["status"], "received",
                             "a reconciliação promoveu o resultado")
            R["publish"](eng, d["draft"])
            self.assertEqual(tarefa(eng, t)["state"], "completed")

    def test_nothing_to_reconcile_publishes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            W["task_plan"](eng, "x", ["c"])
            antes = (eng / CP).read_bytes()
            self.assertEqual(W["tasks_reconcile"](eng)["changed"], [])
            self.assertEqual((eng / CP).read_bytes(), antes)


class T12_FalhaComCheckpoint(unittest.TestCase):

    def test_a_crash_before_the_receipt_is_recovered_to_the_new_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t, d = lente(eng)
            og = O["run"].__globals__
            real = og["_finish"]

            def morre(*a, **k):
                raise RuntimeError("morre antes do recibo")

            og["_finish"] = morre
            try:
                with self.assertRaises(RuntimeError):
                    R["publish"](eng, d["draft"])
            finally:
                og["_finish"] = real
                O["release"](eng, {"pid": os.getpid(),
                                   "started": O["_proc_started"](os.getpid())})
            self.assertFalse(B["bootstrap"](eng)["ready"])
            O["recover"](eng)
            self.assertTrue(B["bootstrap"](eng)["ready"])
            self.assertEqual(tarefa(eng, t)["state"], "completed")
            self.assertIn("C-050", (eng / SU).read_text(encoding="utf-8"))


class Integridade(unittest.TestCase):

    def test_an_unreadable_checkpoint_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            (eng / "_work").mkdir()
            (eng / CP).write_text("{ não é json", encoding="utf-8")
            with self.assertRaises(W["WorkflowError"]) as ctx:
                W["task_plan"](eng, "x", ["c"])
            self.assertEqual(ctx.exception.code, "INTEGRITY_FAILURE")
            self.assertEqual((eng / CP).read_text(encoding="utf-8"), "{ não é json")

    def test_a_future_schema_is_refused_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            (eng / "_work").mkdir()
            (eng / CP).write_text(json.dumps({"schema_version": "handoff-work/9"}),
                                  encoding="utf-8")
            with self.assertRaises(W["WorkflowError"]) as ctx:
                W["read_checkpoint"](eng)
            self.assertEqual(ctx.exception.code, "SCHEMA_UNSUPPORTED")

    def test_a_task_needs_a_closing_criterion_and_known_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            with self.assertRaises(W["WorkflowError"]):
                W["task_plan"](eng, "x", [])
            with self.assertRaises(W["WorkflowError"]):
                W["task_plan"](eng, "x", ["c"], depends=["TASK-099"])

    def test_a_draft_for_a_task_that_did_not_start_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            t = W["task_plan"](eng, "x", ["c"])["task"]
            with self.assertRaises(R["ResolveError"]) as ctx:
                R["draft"](eng, [SU], task=t)
            self.assertEqual(ctx.exception.code, "TASK_NOT_RUNNING")

    def test_the_checkpoint_is_coordinated_state_for_the_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            W["task_plan"](eng, "x", ["c"])
            payload = {"tool_name": "Write",
                       "tool_input": {"file_path": str(eng / CP), "content": "{}"}}
            p = subprocess.run([sys.executable,
                                str(ROOT / ".claude" / "hooks" / "pre-authority-guard.py")],
                               input=json.dumps(payload), capture_output=True, text=True,
                               env=dict(os.environ, AISA_ENGAGEMENTS_ROOT=str(eng.parent),
                                        AISA_GUARD_MODE="enforce"))
            self.assertEqual(p.returncode, 2, p.stderr)


class CLI(unittest.TestCase):

    def test_plan_start_from_the_command_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            p = subprocess.run([sys.executable, str(TOOLS / "workflow.py"), "task", "plan",
                                "--engagement", str(eng), "--role", "lens-user",
                                "--criteria", "linhas publicadas", "--input", "answers.md",
                                "--start", "--json"], capture_output=True, text=True,
                               timeout=300, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)["task"], "TASK-001")
            self.assertEqual(tarefa(eng, "TASK-001")["state"], "running")

    def test_a_refusal_prints_the_stable_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            p = subprocess.run([sys.executable, str(TOOLS / "workflow.py"), "task", "start",
                                "TASK-404", "--engagement", str(eng)],
                               capture_output=True, text=True, timeout=300,
                               env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            self.assertEqual(p.returncode, 1)
            self.assertEqual(json.loads(p.stderr)["code"], "INTEGRITY_FAILURE")


if __name__ == "__main__":
    unittest.main()
