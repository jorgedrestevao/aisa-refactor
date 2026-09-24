# -*- coding: utf-8 -*-
"""handoff-v1 F1.6 — T08: agentes concordam sem evidência, o estado não sobe.

Regra (library/kernel/states.md → Confirmed threshold; orchestration.md → Dialectic round):
`Confirmed` só com um localizador das classes do limiar e o alvo presente. Quantas personas
concordam nunca muda um estado epistémico, e uma síntese dialéctica resolve recomendações,
nunca factos.

A garantia não fica em prosa: num engagement handoff-v1, `pre-authority-guard.py` recusa a
escrita na SU que acrescente, ou promova no lugar (F0 D19), uma linha `Confirmed` sem
localizador. Aqui corre o hook real, em subprocesso, sobre engagements sintéticos.
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
HOOK = ROOT / ".claude" / "hooks" / "pre-authority-guard.py"
M = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "migrate.py"))
ESTADO_HANDOFF = runpy.run_path(str(ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1"
                                  / "estado.py"))["estado"]

CAB = """# Shared Understanding — eng

## Confirmed

| id | lens | claim | evidência | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|
{c}
## Unknown

| id | lens | pergunta | tipo | impacto | âmbito | quem responde | fecho | bloqueio | criticidade | custo | swing | referências | ronda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
{u}
## Assumed

| id | lens | claim | base da assumption | verificado_em | validade | ronda |
|---|---|---|---|---|---|---|
{a}"""

U1 = ("| U-001 | business | Qual é o limiar? | fact_gap | funcional: muda o roteamento | "
      "aprovação | role: direcção financeira | valor do despacho | blocks_scope | Critical | "
      "documento | dimensionante: o valor define quem aprova | sources/c.md#C4 | F-01 |\n")
POR_CONSENSO = ("| C-001 | chair | O limiar é 5 000 € | anchored by business-analyst, "
                "cfo-lens, operations-lead (três personas concordam) | 2026-09-23 | "
                "organizacional | F-01 |\n")
COM_LOCATOR = ("| C-001 | chair | O dono declara que o limiar é 5 000 € | declaração do dono "
               "do processo, 2026-09-23 — answers.md#U-001 | 2026-09-23 | organizacional | "
               "F-01 |\n")


def su(c="", u="", a=""):
    return CAB.format(c=c, u=u, a=a)


def engagement(base):
    eng = base / "eng"
    eng.mkdir()
    M["init"](eng)
    (eng / "_state.json").write_text(ESTADO_HANDOFF(engagement="eng", phase="framing"),
                                     encoding="utf-8")
    (eng / "answers.md").write_text("# Answers — eng\n\n## U-001 — 2026-09-23\n\n"
                                    "«O limiar é 5 000 €.»\n", encoding="utf-8")
    (eng / "decisions.md").write_text("# Decisions — eng\n", encoding="utf-8")
    (eng / "shared-understanding.md").write_text(su(u=U1), encoding="utf-8")
    # o grafo espelha a SU, como o `on-su-mirror` o deixaria
    R = runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "resolve.py"))
    R["sync_mirror"](eng)
    return eng


def corre(base, payload, modo=None):
    env = dict(os.environ, AISA_ENGAGEMENTS_ROOT=str(base))
    env.pop("AISA_GUARD_MODE", None)
    if modo:
        env["AISA_GUARD_MODE"] = modo
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8", env=env)


def negou(p):
    if p.returncode != 2:
        return False
    try:
        out = json.loads(p.stderr.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return False
    return out.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"


def razao(p):
    try:
        return json.loads(p.stderr.strip().splitlines()[-1])["hookSpecificOutput"][
            "permissionDecisionReason"]
    except (ValueError, IndexError, KeyError):
        return p.stderr


def write(eng, content):
    return {"tool_name": "Write", "tool_input": {
        "file_path": str(eng / "shared-understanding.md"), "content": content}}


class T08_ConcordanciaNaoEEvidencia(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.eng = engagement(self.base)

    def tearDown(self):
        self.tmp.cleanup()

    def test_personas_agreeing_do_not_make_a_confirmed_row(self):
        p = corre(self.base, write(self.eng, su(c=POR_CONSENSO, u=U1)))
        self.assertTrue(negou(p), p.stderr)
        self.assertIn("C-001", razao(p))
        self.assertIn("concordância entre personas não é evidência", razao(p))

    def test_the_same_claim_with_a_locator_passes(self):
        p = corre(self.base, write(self.eng, su(c=COM_LOCATOR, u=U1)))
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_a_locator_whose_target_is_missing_is_refused_too(self):
        sem_alvo = COM_LOCATOR.replace("answers.md#U-001", "answers.md#U-099")
        p = corre(self.base, write(self.eng, su(c=sem_alvo, u=U1)))
        self.assertTrue(negou(p), p.stderr)

    def test_the_agreement_written_as_assumed_passes(self):
        a = ("| A-001 | chair | O limiar é 5 000 € | três personas concordam (business-analyst, "
             "cfo-lens, operations-lead); sem documento | 2026-09-23 | organizacional | F-01 |\n")
        p = corre(self.base, write(self.eng, su(u=U1, a=a)))
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_an_in_place_promotion_with_the_same_id_is_refused(self):
        """F0 D19: a pergunta passa para `## Confirmed` com o mesmo id e sem transição."""
        promovida = ("| U-001 | business | O limiar é 5 000 € | o council concorda | "
                     "2026-09-23 | organizacional | F-01 |\n")
        p = corre(self.base, write(self.eng, su(c=promovida)))
        self.assertTrue(negou(p), p.stderr)
        self.assertIn("U-001", razao(p))

    def test_swapping_the_evidence_of_an_existing_row_for_agreement_is_refused(self):
        (self.eng / "shared-understanding.md").write_text(su(c=COM_LOCATOR, u=U1),
                                                          encoding="utf-8")
        runpy.run_path(str(ROOT / "library" / "kernel" / "tools" / "resolve.py"))[
            "sync_mirror"](self.eng)
        payload = {"tool_name": "Edit", "tool_input": {
            "file_path": str(self.eng / "shared-understanding.md"),
            "old_string": "declaração do dono do processo, 2026-09-23 — answers.md#U-001",
            "new_string": "anchored by business-analyst, cfo-lens"}}
        self.assertTrue(negou(corre(self.base, payload)))

    def test_an_edit_that_touches_no_confirmed_row_passes(self):
        payload = {"tool_name": "Edit", "tool_input": {
            "file_path": str(self.eng / "shared-understanding.md"),
            "old_string": "Qual é o limiar?", "new_string": "Qual é o limiar da direcção?"}}
        self.assertEqual(corre(self.base, payload).returncode, 0)

    def test_the_override_stays_explicit(self):
        p = corre(self.base, write(self.eng, su(c=POR_CONSENSO, u=U1)), modo="log")
        self.assertEqual(p.returncode, 0)
        self.assertIn("(log)", p.stderr)


class T08_ContratoDoChairman(unittest.TestCase):
    """O chairman deixou de promover por contagem (F0 D03)."""

    CHAIR = (ROOT / ".claude" / "skills" / "chairman-synthesis" / "SKILL.md").read_text(
        encoding="utf-8")
    AGENT = (ROOT / ".claude" / "agents" / "chairman.md").read_text(encoding="utf-8")
    ORCH = (ROOT / "library" / "kernel" / "orchestration.md").read_text(encoding="utf-8")

    def test_no_head_count_path_to_confirmed_remains(self):
        self.assertNotIn("must have ≥2 persona anchors", self.CHAIR)
        self.assertNotIn("often becomes Confirmed", self.AGENT)
        self.assertNotIn("Overlap with ≥2 anchors AND each anchor", self.CHAIR)
        self.assertNotIn("resolved by an accepted synthesis become normal rows", self.CHAIR)

    def test_the_rule_is_stated_where_rows_are_written(self):
        self.assertIn("A Confirmed row needs a locator, never a head-count", self.CHAIR)
        self.assertIn("agreement, not evidence", self.AGENT)

    def test_t30_contract_a_synthesis_settles_recommendations_and_escalates_at_the_cap(self):
        flat = " ".join(self.ORCH.split())
        self.assertIn("settles a recommendation, a ranking or a disposition — never a fact", flat)
        self.assertIn("never accepted by exhaustion", flat)
        self.assertIn("escalated, never accepted by exhaustion", " ".join(self.CHAIR.split()))


if __name__ == "__main__":
    unittest.main(verbosity=1)
