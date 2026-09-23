# -*- coding: utf-8 -*-
"""handoff-v1 F1.4 — o legado so se le, e a versao historica nao escreve no novo.

Decisao classic A: a versao nova nao tem runtime classic. Um engagement sem bloco
`workflow` em `_state.json` e da versao historica (`jorgedrestevao/aisa@85baf10`): aqui le-se
e nao se escreve, por nenhuma das camadas (Skill, Write/Edit, coordenador, bootstrap).
Decisao Q1: os engagements novos nascem com grafo schema 2, que a versao historica recusa
pelos seus proprios guardas.

- T03  engagement sem perfil: identificado, recusado em todas as camadas, dados intactos,
       leitura possivel.
- T36  leitor antigo encontra schema novo: o codigo historico REAL (extraido do commit
       `ba0c27b`, arvore igual a `85baf10`) recusa escrever num engagement novo.
- D05 e I-07  estado coordenado nunca por ferramenta; `_state.json` nao perde chaves nem
       muda de perfil por ferramenta; o `.tmp` das skills e guardado como o original.
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
HOOKS = ROOT / ".claude" / "hooks"
ESTADO_HANDOFF = runpy.run_path(str(ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1"
                                  / "estado.py"))["estado"]
O = runpy.run_path(str(TOOLS / "operation.py"))
B = runpy.run_path(str(TOOLS / "bootstrap.py"))
G = runpy.run_path(str(TOOLS / "graph.py"))
M = runpy.run_path(str(TOOLS / "migrate.py"))
HISTORICO = "ba0c27b"

SU = """# Shared Understanding — eng

## Confirmed

| id | lens | claim | evidência | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|
| C-001 | data | facto | fonte: inicial | 2026-01-01 | organizacional | R-01 |
"""
NOS = [{"id": "C-001", "type": "su-row",
        "props": {"state": "Confirmed", "text": "facto", "resolved": False, "criticidade": ""},
        "provenance": {"mirror_of": "SU:C-001"}}]


def escreve_grafo(eng, schema):
    body, meta = G["serialize"](NOS, [])
    meta = json.loads(meta)
    meta["schema_version"] = schema
    (eng / "_graph").mkdir(exist_ok=True)
    (eng / "_graph" / "graph.jsonl").write_text(body, encoding="utf-8", newline="\n")
    (eng / "_graph" / "meta.json").write_text(json.dumps(meta), encoding="utf-8", newline="\n")


def legado(base, nome="velho", com_grafo=True):
    """Um engagement como a versao historica o deixa: sem `workflow`, grafo schema 1."""
    eng = base / nome
    eng.mkdir(parents=True)
    (eng / "_state.json").write_text('{"engagement":"velho","pack":"pp","phase":"discovery",'
                                     '"round":"R-01"}\n', encoding="utf-8", newline="\n")
    (eng / "shared-understanding.md").write_text(SU, encoding="utf-8", newline="\n")
    (eng / "decisions.md").write_text("# Decisions\n", encoding="utf-8", newline="\n")
    (eng / "answers.md").write_text("# Answers\n", encoding="utf-8", newline="\n")
    if com_grafo:
        escreve_grafo(eng, 1)
    return eng


def novo(base, nome="novo"):
    """Um engagement handoff-v1: `workflow` no estado e grafo publicado por esta versao."""
    eng = base / nome
    eng.mkdir(parents=True)
    M["init"](eng)
    (eng / "_state.json").write_text(ESTADO_HANDOFF(engagement=nome, phase="discovery",
                                                    round="R-01"), encoding="utf-8",
                                     newline="\n")
    (eng / "shared-understanding.md").write_text(SU.replace("| C-001 | data | facto | fonte: "
                                                            "inicial | 2026-01-01 | "
                                                            "organizacional | R-01 |\n", ""),
                                                 encoding="utf-8", newline="\n")
    (eng / "decisions.md").write_text("# Decisions\n", encoding="utf-8", newline="\n")
    (eng / "answers.md").write_text("# Answers\n", encoding="utf-8", newline="\n")
    return eng


def pegada(eng):
    return {str(p.relative_to(eng)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(eng.rglob("*")) if p.is_file()}


def hook(nome, payload, base, hooks_dir=HOOKS, modo=None):
    env = dict(os.environ, AISA_ENGAGEMENTS_ROOT=str(base))
    env.pop("AISA_GUARD_MODE", None)
    if modo:
        env["AISA_GUARD_MODE"] = modo
    return subprocess.run([sys.executable, str(hooks_dir / nome)], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8", env=env)


def negou(p):
    if p.returncode != 2:
        return False
    try:
        out = json.loads(p.stderr.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return False
    return out.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"


def write(path, content=None):
    ti = {"file_path": str(path)}
    if content is not None:
        ti["content"] = content
    return {"tool_name": "Write", "tool_input": ti}


def skill(nome, args=""):
    return {"tool_name": "Skill", "tool_input": {"skill": nome, "args": args}}


class Base(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()


class T03_LegadoSoSeLe(Base):

    def test_every_authority_write_is_refused_and_nothing_changes(self):
        eng = legado(self.base)
        antes = pegada(eng)
        for nome in ("shared-understanding.md", "decisions.md", "answers.md", "_state.json",
                     "_state.json.tmp"):
            p = hook("pre-authority-guard.py", write(eng / nome, "{}"), self.base)
            self.assertTrue(negou(p), "`{}` passou num engagement legado".format(nome))
            self.assertIn("aisa@85baf10", p.stderr)
        self.assertEqual(pegada(eng), antes)

    def test_a_legacy_engagement_without_graph_is_refused_too(self):
        eng = legado(self.base, com_grafo=False)
        p = hook("pre-authority-guard.py", write(eng / "shared-understanding.md", "x"), self.base)
        self.assertTrue(negou(p))

    def test_the_coordinator_refuses_to_publish_and_writes_nothing(self):
        eng = legado(self.base)
        antes = pegada(eng)
        with self.assertRaises(O["OperationError"]) as ctx:
            O["run"](eng, "op-legado", {"shared-understanding.md": "novo\n"})
        self.assertEqual(ctx.exception.code, "UNSUPPORTED_PROFILE")
        self.assertEqual(pegada(eng), antes)

    def test_the_coordinator_refuses_to_recover_a_legacy_pending_operation(self):
        eng = legado(self.base)
        intent = {"intent_version": 1, "operation_id": "op-velha", "request_hash": "h",
                  "owner": {}, "before": {}, "after": {}, "staging": "_ops/staging/op-velha"}
        O["_atomic_write"](O["pending_path"](eng), json.dumps(intent))
        antes = pegada(eng)
        with self.assertRaises(O["OperationError"]) as ctx:
            O["recover"](eng)
        self.assertEqual(ctx.exception.code, "UNSUPPORTED_PROFILE")
        self.assertEqual(pegada(eng), antes)

    def test_migrating_a_legacy_engagement_is_refused(self):
        eng = legado(self.base, com_grafo=False)
        antes = pegada(eng)
        with self.assertRaises(M["MigrationError"]) as ctx:
            M["apply"](eng)
        self.assertEqual(ctx.exception.code, "UNSUPPORTED_PROFILE")
        self.assertEqual(pegada(eng), antes)

    def test_the_bootstrap_is_not_ready_and_says_why(self):
        boot = B["bootstrap"](legado(self.base))
        self.assertFalse(boot["ready"])
        self.assertEqual(boot["limitations"][0]["code"], "UNSUPPORTED_PROFILE")
        self.assertIn("aisa@85baf10", boot["limitations"][0]["recovery"])

    def test_a_write_skill_is_refused_before_it_starts(self):
        eng = legado(self.base)
        antes = pegada(eng)
        for nome in ("aisa-round", "aisa-capture", "lens-data", "chairman-synthesis"):
            p = hook("pre-profile-check.py", skill(nome, "--engagement velho"), self.base)
            self.assertTrue(negou(p), nome)
            self.assertIn("aisa@85baf10", p.stderr)
        self.assertEqual(pegada(eng), antes)

    def test_reading_skills_still_run_on_a_legacy_engagement(self):
        legado(self.base)
        for nome in ("aisa-status", "aisa-orient"):
            p = hook("pre-profile-check.py", skill(nome, "--engagement velho"), self.base)
            self.assertEqual(p.returncode, 0, nome)

    def test_an_unnamed_engagement_among_several_is_not_guessed(self):
        legado(self.base)
        novo(self.base)
        p = hook("pre-profile-check.py", skill("aisa-round"), self.base)
        self.assertEqual(p.returncode, 0)
        self.assertIn("nenhum nomeado", p.stderr)

    def test_the_status_model_still_reads_a_legacy_engagement(self):
        eng = legado(self.base)
        antes = pegada(eng)
        from datetime import date
        D = runpy.run_path(str(TOOLS / "dashboard.py"))
        model = D["build_model"](eng, date(2026, 9, 23))
        self.assertIn("C-001", json.dumps(model, ensure_ascii=False, default=str))
        self.assertEqual(pegada(eng), antes)

    def test_the_override_stays_explicit(self):
        eng = legado(self.base)
        p = hook("pre-authority-guard.py", write(eng / "decisions.md", "x"), self.base,
                 modo="log")
        self.assertEqual(p.returncode, 0)
        self.assertIn("(log)", p.stderr)


class T03_NovoEscreve(Base):

    def test_a_handoff_engagement_is_ready_and_lets_authorities_through(self):
        eng = novo(self.base)
        self.assertTrue(B["bootstrap"](eng)["ready"])
        for nome in ("shared-understanding.md", "decisions.md", "answers.md"):
            p = hook("pre-authority-guard.py", write(eng / nome, "x"), self.base)
            self.assertEqual(p.returncode, 0, "{}: {}".format(nome, p.stderr))
        p = hook("pre-profile-check.py", skill("aisa-round", "--engagement novo"), self.base)
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_the_graph_of_a_new_engagement_is_schema_2(self):
        eng = novo(self.base)
        meta = json.loads((eng / "_graph" / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["schema_version"], 2)

    def test_a_schema_1_graph_is_named_as_the_historical_version(self):
        st = G["read"](legado(self.base))
        self.assertEqual(st["status"], G["UNSUPPORTED_SCHEMA"])
        self.assertIn("versão histórica", st["detail"])


class D05_EstadoCoordenado(Base):

    def test_no_tool_writes_into_coordinated_state_even_when_ready(self):
        eng = novo(self.base)
        self.assertTrue(B["bootstrap"](eng)["ready"])
        for rel in ("_graph/graph.jsonl", "_ops/pending.json", "_migration/manifest.json",
                    "_work/checkpoint.json", "_design/functional-contracts.json"):
            p = hook("pre-authority-guard.py", write(eng / rel, "{}"), self.base)
            self.assertTrue(negou(p), "`{}` passou".format(rel))


class I07_EstadoSemPerdas(Base):

    def setUp(self):
        super().setUp()
        self.eng = novo(self.base)
        self.estado = json.loads((self.eng / "_state.json").read_text(encoding="utf-8"))

    def test_changing_the_round_passes(self):
        e = dict(self.estado, round="R-02")
        for nome in ("_state.json", "_state.json.tmp"):
            p = hook("pre-authority-guard.py", write(self.eng / nome, json.dumps(e)), self.base)
            self.assertEqual(p.returncode, 0, "{}: {}".format(nome, p.stderr))

    def test_dropping_a_key_is_refused(self):
        e = {k: v for k, v in self.estado.items() if k != "phase"}
        for nome in ("_state.json", "_state.json.tmp"):
            p = hook("pre-authority-guard.py", write(self.eng / nome, json.dumps(e)), self.base)
            self.assertTrue(negou(p), nome)
            self.assertIn("`phase`", p.stderr)

    def test_changing_the_profile_block_by_tool_is_refused(self):
        e = json.loads(json.dumps(self.estado))
        e["workflow"]["route"] = "change-impact"
        p = hook("pre-authority-guard.py", write(self.eng / "_state.json.tmp", json.dumps(e)),
                 self.base)
        self.assertTrue(negou(p))

    def test_an_edit_that_changes_the_route_is_refused(self):
        texto = (self.eng / "_state.json").read_text(encoding="utf-8")
        payload = {"tool_name": "Edit", "tool_input": {
            "file_path": str(self.eng / "_state.json"),
            "old_string": '"route": "solution-choice"',
            "new_string": '"route": "platform-constrained"'}}
        self.assertIn('"route": "solution-choice"', texto)
        self.assertTrue(negou(hook("pre-authority-guard.py", payload, self.base)))

    def test_new_content_that_is_not_json_is_refused(self):
        p = hook("pre-authority-guard.py", write(self.eng / "_state.json", "{ nao"), self.base)
        self.assertTrue(negou(p))


class D02_EstadoSoLe(unittest.TestCase):
    """`/status`, `/resume` e `aisa-orient` sao leituras (decisao Q6). O guarda ja recusa a
    escrita num legado; isto fixa que a skill deixou de a pedir."""

    STATUS = ROOT / ".claude" / "skills" / "aisa-status" / "SKILL.md"
    START = ROOT / ".claude" / "skills" / "aisa-start" / "SKILL.md"

    def test_the_status_skill_asks_for_no_write(self):
        texto = self.STATUS.read_text(encoding="utf-8")
        self.assertNotIn("Write the SU health header", texto)
        self.assertNotIn("update `> Saúde epistémica", texto)
        self.assertIn("never written into the SU", texto)
        self.assertIn("This skill writes nothing", texto)

    def test_the_start_skeleton_has_no_health_line_to_fill(self):
        texto = self.START.read_text(encoding="utf-8")
        esqueleto = texto[texto.index("8. **Write the `shared-understanding.md` skeleton**"):
                          texto.index("9. Write `council-log.md`")]
        self.assertNotIn("> Saúde epistémica", esqueleto)


class T36_LeitorAntigo(Base):
    """O codigo da versao historica, tal como esta no commit `ba0c27b`, contra um engagement
    criado por esta versao. Nao se assume que respeita um campo que nunca conheceu (07)."""

    @classmethod
    def setUpClass(cls):
        existe = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e",
                                 HISTORICO + "^{commit}"], capture_output=True)
        if existe.returncode != 0:
            raise AssertionError("o commit historico {} nao esta no clone: o CI precisa de "
                                 "`fetch-depth: 0`".format(HISTORICO))
        cls.velho = Path(tempfile.mkdtemp())
        nomes = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--name-only", HISTORICO,
                                "library/kernel/tools/"], capture_output=True, text=True,
                               check=True).stdout.split()
        for rel in [n for n in nomes if n.endswith(".py")] + [
                ".claude/hooks/pre-authority-guard.py"]:
            corpo = subprocess.run(["git", "-C", str(ROOT), "show", "{}:{}".format(HISTORICO, rel)],
                                   capture_output=True, check=True).stdout
            destino = cls.velho / rel
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(corpo)

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.velho, ignore_errors=True)

    def test_the_historical_code_is_the_one_that_reads_schema_1(self):
        velho_g = runpy.run_path(str(self.velho / "library" / "kernel" / "tools" / "graph.py"))
        self.assertEqual(velho_g["SCHEMA_VERSION"], 1)

    def test_the_historical_guard_refuses_to_write_in_a_new_engagement(self):
        eng = novo(self.base)
        antes = pegada(eng)
        for nome in ("shared-understanding.md", "decisions.md", "answers.md", "_state.json"):
            p = hook("pre-authority-guard.py", write(eng / nome, "x"), self.base,
                     hooks_dir=self.velho / ".claude" / "hooks")
            self.assertTrue(negou(p), "a versao historica escreveria em `{}`".format(nome))
        self.assertEqual(pegada(eng), antes)

    def test_the_historical_bootstrap_names_the_unsupported_schema(self):
        eng = novo(self.base)
        vb = runpy.run_path(str(self.velho / "library" / "kernel" / "tools" / "bootstrap.py"))
        boot = vb["bootstrap"](eng)
        self.assertFalse(boot["ready"])
        self.assertEqual(boot["limitations"][0]["code"], "UNSUPPORTED_SCHEMA")

    def test_the_historical_migrate_does_not_replace_the_new_graph(self):
        eng = novo(self.base)
        antes = pegada(eng)
        vm = runpy.run_path(str(self.velho / "library" / "kernel" / "tools" / "migrate.py"))
        with self.assertRaises(Exception):
            vm["init"](eng)
        self.assertEqual(pegada(eng), antes)


if __name__ == "__main__":
    unittest.main(verbosity=1)
