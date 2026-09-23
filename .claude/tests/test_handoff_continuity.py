# -*- coding: utf-8 -*-
"""handoff-v1 F2 — continuidade transacional: read-set, conflito, repetição e falha.

Plano: `docs/handoff-v1/plan/06_VALIDACAO.md` T11–T14, `04_CONTINUIDADE.md`
§Protocolo de publicação. Desenho: `docs/handoff-v1/F2/DESENHO.md` §1–§2.

    T11  input lido muda durante a execução -> STALE_INPUT, rascunho intacto, nada publicado
    T12  falha em cada limite de publicação -> revisão antiga ou nova, ou RECOVERY_REQUIRED;
         nunca uma mistura dada por pronta
    T13  repetir a operação depois do sucesso -> o mesmo recibo, sem duplicar efeitos
    T14  duas sessões publicam da mesma base -> uma publica, a outra recebe conflito; nada
         se perde
    D17  a projecção lê o modelo dentro da janela validada pelo bootstrap

Stdlib apenas. Engagement sintético (`test_migration.make`), nenhum dado real.
"""
import json
import multiprocessing
import os
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
FIX = runpy.run_path(str(ROOT / ".claude" / "tests" / "test_migration.py"))
M = runpy.run_path(str(TOOLS / "migrate.py"))
O = runpy.run_path(str(TOOLS / "operation.py"))
B = runpy.run_path(str(TOOLS / "bootstrap.py"))
P = runpy.run_path(str(TOOLS / "projection.py"))
W = runpy.run_path(str(TOOLS / "workflow.py"))

SU = "shared-understanding.md"


def engagement(tmp):
    projects = Path(tmp) / "projects"
    projects.mkdir()
    eng = Path(FIX["make"](str(projects), FIX["NOVO"]))
    M["apply"](eng)
    assert B["bootstrap"](eng)["ready"], "a premissa do caso caiu"
    return eng


def escreve(eng, rel, texto):
    p = eng / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8", newline="\n")


class T11_ReadSet(unittest.TestCase):
    """O que se leu e não se escreve também é pré-condição (D08)."""

    def test_a_changed_read_only_input_is_stale_and_nothing_is_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            escreve(eng, "frame.md", "# frame v1\n")
            lido = {"frame.md": O["digest"](eng / "frame.md")}
            base = {"answers.md": O["digest"](eng / "answers.md")}
            rascunho = "# Respostas\n\nconclusão tirada do frame v1\n"
            escreve(eng, "frame.md", "# frame v2 — mudou durante a tarefa\n")
            antes = (eng / "answers.md").read_bytes() if (eng / "answers.md").exists() else b""
            with self.assertRaises(O["OperationError"]) as ctx:
                O["run"](eng, "t11", {"answers.md": rascunho}, expected=base, read_set=lido)
            self.assertEqual(ctx.exception.code, "STALE_INPUT")
            self.assertEqual(O["stable_code"](ctx.exception.code), "STALE_INPUT")
            self.assertEqual(ctx.exception.detail["path"], "frame.md")
            depois = (eng / "answers.md").read_bytes() if (eng / "answers.md").exists() else b""
            self.assertEqual(antes, depois, "o alvo mudou apesar da recusa")
            self.assertIsNone(O["read_receipt"](eng, "t11"), "ficou recibo de uma recusa")
            self.assertEqual(O["status"](eng)["state"], O["CLEAN"],
                             "a recusa deixou pendência — devia recusar antes do staging")
            self.assertFalse((eng / "_ops" / "staging" / "t11").exists())

    def test_an_unchanged_read_only_input_publishes_and_the_receipt_records_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            escreve(eng, "frame.md", "# frame v1\n")
            lido = {"frame.md": O["digest"](eng / "frame.md")}
            r = O["run"](eng, "t11-ok", {"notas.md": "x\n"}, expected={"notas.md": ""},
                         read_set=lido)
            self.assertEqual(r["result"], "committed")
            self.assertEqual(r["read_set"], lido)

    def test_a_read_set_absence_is_a_state(self):
        """Ler «não existe» e o ficheiro aparecer entretanto também é input mudado."""
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            lido = {"options.md": ""}
            escreve(eng, "options.md", "# apareceu\n")
            with self.assertRaises(O["OperationError"]) as ctx:
                O["run"](eng, "t11-aus", {"notas.md": "x\n"}, read_set=lido)
            self.assertEqual(ctx.exception.code, "STALE_INPUT")

    def test_a_path_cannot_be_read_and_written_in_the_same_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            with self.assertRaises(O["OperationError"]) as ctx:
                O["run"](eng, "t11-dup", {"notas.md": "x\n"}, read_set={"notas.md": ""})
            self.assertEqual(ctx.exception.code, "READ_SET_OVERLAP")

    def test_the_request_identity_includes_the_read_set(self):
        ws = {"a.md": "x"}
        self.assertEqual(O["request_hash"](ws), O["request_hash"](ws, None),
                         "sem read-set, o hash mudou — recibos antigos deixavam de bater")
        self.assertNotEqual(O["request_hash"](ws, {"b.md": "1" * 64}),
                            O["request_hash"](ws, {"b.md": "2" * 64}))


class T13_Repeticao(unittest.TestCase):
    """Sucesso sem resposta: repetir devolve o mesmo recibo e não escreve outra vez."""

    def test_repeating_after_success_returns_the_same_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            ws = {"notas.md": "linha única\n"}
            r1 = O["run"](eng, "t13", ws, expected={"notas.md": ""})
            mtime = (eng / "notas.md").stat().st_mtime_ns
            r2 = O["run"](eng, "t13", ws, expected={"notas.md": ""})
            self.assertTrue(r2["replayed"])
            self.assertTrue(r2["effects_present"])
            self.assertEqual(r1["revision"], r2["revision"])
            self.assertEqual(r1["committed_at"], r2["committed_at"])
            self.assertEqual((eng / "notas.md").stat().st_mtime_ns, mtime,
                             "a repetição voltou a escrever")
            self.assertEqual((eng / "notas.md").read_text(encoding="utf-8"), "linha única\n")

    def test_same_id_with_a_different_request_is_an_integrity_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            O["run"](eng, "t13b", {"notas.md": "a\n"})
            with self.assertRaises(O["OperationError"]) as ctx:
                O["run"](eng, "t13b", {"notas.md": "b\n"})
            self.assertEqual(O["stable_code"](ctx.exception.code), "INTEGRITY_FAILURE")


def _sessao(eng, op_id, texto, base, barreira, fila):
    """Uma sessão que leu a mesma base que a outra e publica."""
    barreira.wait()
    try:
        r = O["run"](Path(eng), op_id, {"notas.md": texto}, expected={"notas.md": base})
        fila.put(("ok", op_id, r["result"]))
    except O["OperationError"] as exc:
        fila.put(("erro", op_id, exc.code))


class T14_DuasSessoes(unittest.TestCase):

    @unittest.skipIf(os.name == "nt", "processos reais por fork; em Windows o harness de "
                                      "concorrência é test_operation_concurrency")
    def test_same_base_one_publishes_the_other_gets_an_explicit_conflict(self):
        ctx = multiprocessing.get_context("fork")
        for corrida in range(4):
            with tempfile.TemporaryDirectory() as tmp:
                eng = engagement(tmp)
                escreve(eng, "notas.md", "base\n")
                base = O["digest"](eng / "notas.md")
                barreira, fila = ctx.Barrier(2), ctx.Queue()
                ps = [ctx.Process(target=_sessao,
                                  args=(str(eng), "s{}".format(i), "sessão {}\n".format(i),
                                        base, barreira, fila)) for i in (1, 2)]
                for p in ps:
                    p.start()
                for p in ps:
                    p.join(60)
                res = [fila.get(timeout=5) for _ in ps]
                ok = [r for r in res if r[0] == "ok"]
                erros = [r for r in res if r[0] == "erro"]
                self.assertEqual(len(ok), 1, "corrida {}: {}".format(corrida, res))
                self.assertEqual(len(erros), 1, "corrida {}: {}".format(corrida, res))
                # quem perdeu viu conflito, não uma escrita calada
                self.assertIn(O["stable_code"](erros[0][2]),
                              ("STALE_INPUT", "CONCURRENT_WRITE"), res)
                vencedor = ok[0][1]
                self.assertEqual((eng / "notas.md").read_text(encoding="utf-8"),
                                 "sessão {}\n".format(vencedor[1]),
                                 "o ficheiro não tem o que o recibo committed diz")
                self.assertEqual(O["status"](eng)["state"], O["CLEAN"])


class T12_FalhaEmCadaLimite(unittest.TestCase):
    """Uma operação de três ficheiros morre em cada limite da publicação.

    Limites: depois do marcador e antes do primeiro alvo; depois de 1 e de 2 alvos;
    depois dos 3 e antes do recibo; depois do recibo e antes de retirar o marcador.
    Em todos, o leitor (bootstrap e projecção) recusa-se a dar pronto até à recuperação,
    e a recuperação acaba na revisão NOVA inteira, com um recibo."""

    ALVOS = ("answers.md", "decisions.md", "notas.md")

    def _pedido(self, eng):
        ws = {rel: "{} — revisão nova\n".format(rel) for rel in self.ALVOS}
        exp = {rel: O["digest"](eng / rel) for rel in self.ALVOS}
        return ws, exp

    def _morre(self, eng, limite):
        ws, exp = self._pedido(eng)
        og = O["run"].__globals__
        real_aw, real_fin = og["_atomic_write"], og["_finish"]
        escritos = []

        def aw(p, texto):
            p = Path(p)
            alvo = p.parent.resolve() == eng.resolve() and p.name in self.ALVOS
            if alvo and isinstance(limite, int) and len(escritos) == limite:
                raise RuntimeError("morre antes do alvo {}".format(limite + 1))
            real_aw(p, texto)
            if alvo:
                escritos.append(p.name)
            if limite == "receipt" and "receipts" in p.parts:
                raise RuntimeError("morre depois do recibo")

        def fin(e, intent, published):
            if limite == "before-receipt":
                raise RuntimeError("morre antes do recibo")
            return real_fin(e, intent, published)

        og["_atomic_write"], og["_finish"] = aw, fin
        try:
            with self.assertRaises(RuntimeError):
                O["run"](eng, "t12", ws, expected=exp)
        finally:
            og["_atomic_write"], og["_finish"] = real_aw, real_fin
            O["release"](eng, {"pid": os.getpid(), "started": O["_proc_started"](os.getpid())})
        return ws

    def test_every_boundary_is_old_new_or_recovery_required_never_mixed(self):
        for limite in (0, 1, 2, "before-receipt", "receipt"):
            with self.subTest(limite=limite), tempfile.TemporaryDirectory() as tmp:
                eng = engagement(tmp)
                ws = self._morre(eng, limite)
                boot = B["bootstrap"](eng)
                self.assertFalse(boot["ready"], "limite {}: pronto sobre publicação "
                                                "a meio".format(limite))
                codigos = [l["code"] for l in boot["limitations"]]
                self.assertIn("PENDING_OPERATION", codigos)
                self.assertEqual(O["stable_code"]("PENDING_EXISTS"), "RECOVERY_REQUIRED")
                proj = P["operational_state"](eng)
                self.assertFalse(proj["ready"])
                self.assertFalse(proj["gate"].get("open"))
                with self.assertRaises(O["OperationError"]) as ctx:
                    O["run"](eng, "outra", {"x.md": "y"})
                self.assertEqual(O["stable_code"](ctx.exception.code), "RECOVERY_REQUIRED")

                rec = O["recover"](eng)
                self.assertIn(rec["result"], ("rolled_forward",))
                for rel, texto in ws.items():
                    self.assertEqual((eng / rel).read_text(encoding="utf-8"), texto,
                                     "limite {}: {} ficou na revisão velha".format(
                                         limite, rel))
                self.assertEqual(O["status"](eng)["state"], O["CLEAN"])
                self.assertEqual(O["recover"](eng)["result"], "nothing_pending",
                                 "recuperar outra vez mudou alguma coisa")
                self.assertEqual(O["read_receipt"](eng, "t12")["result"], "committed")


class D17_ProjeccaoNumaRevisao(unittest.TestCase):

    def test_a_write_between_bootstrap_and_model_is_never_projected(self):
        """Uma escrita entre o bootstrap e o modelo repete a leitura; a mexer sempre,
        bloqueia com CONCURRENT_WRITE e não projecta."""
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            real = P["_D"]["build_model"]
            chamadas = []

            def modelo_com_escritor(e, today):
                chamadas.append(1)
                escreve(eng, "frame.md", "# frame {}\n".format(len(chamadas)))
                return real(e, today)

            P["_D"]["build_model"] = modelo_com_escritor
            try:
                out = P["operational_state"](eng)
            finally:
                P["_D"]["build_model"] = real
            self.assertFalse(out["ready"])
            self.assertIn("CONCURRENT_WRITE", [b["kind"] for b in out["blockers"]])
            self.assertEqual(len(chamadas), P["READ_TRIES"])

    def test_a_single_write_is_absorbed_by_one_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            real = P["_D"]["build_model"]
            chamadas = []

            def modelo_com_uma_escrita(e, today):
                chamadas.append(1)
                if len(chamadas) == 1:
                    escreve(eng, "options.md", "# opções\n")
                return real(e, today)

            P["_D"]["build_model"] = modelo_com_uma_escrita
            try:
                out = P["operational_state"](eng)
            finally:
                P["_D"]["build_model"] = real
            self.assertTrue(out["ready"], out["blockers"])
            self.assertEqual(len(chamadas), 2)

    def test_declared_inputs_enter_the_consumed_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            b1 = B["bootstrap"](eng, inputs=("frame.md", "_blueprint/*.yaml"))
            self.assertEqual(b1["snapshot"]["inputs"], {"frame.md": ""})
            escreve(eng, "_blueprint/ux-blueprint_v01.yaml", "a: 1\n")
            b2 = B["bootstrap"](eng, inputs=("frame.md", "_blueprint/*.yaml"))
            self.assertIn("_blueprint/ux-blueprint_v01.yaml", b2["snapshot"]["inputs"])
            self.assertNotEqual(b1["snapshot"]["input_revision"],
                                b2["snapshot"]["input_revision"])
            self.assertEqual(b1["snapshot"]["revision"], b2["snapshot"]["revision"],
                             "`revision` das autoridades mudou por um input")

    def test_receipts_logs_and_drafts_never_enter_the_read_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            eng = engagement(tmp)
            got = B["expand_inputs"](eng, ("_ops/receipts/x.json", "_drafts/d/a.md",
                                           "_migration/m", SU, "frame.md"))
            self.assertEqual(got, ["frame.md"])


class CodigosEstaveis(unittest.TestCase):

    def test_every_source_code_maps_to_a_contract_code(self):
        contrato = {W["UNSUPPORTED_PROFILE"], W["STALE_INPUT"], W["INCOMPLETE_READ_SET"],
                    W["AUTHORIZATION_REQUIRED"], W["INTEGRITY_FAILURE"],
                    W["SCHEMA_UNSUPPORTED"], W["BLOCKING_GAP"], W["RECOVERY_REQUIRED"],
                    "CONCURRENT_WRITE"}
        for origem, estavel in O["STABLE_CODES"].items():
            self.assertIn(estavel, contrato, origem)
        self.assertEqual(O["stable_code"]("DESCONHECIDO"), "INTEGRITY_FAILURE")

    def test_the_error_envelope_validates_against_handoff_response(self):
        exc = O["OperationError"]("input mudou", "STALE_INPUT",
                                  {"path": "frame.md", "paths": [{"path": "frame.md"}]})
        env = O["response_from_error"](exc, input_revision="abc")
        erros, desconhecidos = W["validate"](env, W["load_schema"]("handoff-response"))
        self.assertEqual(erros, [])
        self.assertEqual(desconhecidos, [])
        self.assertEqual(env["code"], "STALE_INPUT")
        self.assertEqual(env["affected_ids"], ["frame.md"])
        self.assertEqual(env["reasons"][0]["source_code"], "STALE_INPUT")


if __name__ == "__main__":
    unittest.main()
