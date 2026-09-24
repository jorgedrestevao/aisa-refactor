# -*- coding: utf-8 -*-
"""handoff-v1 F8.1 — cada motor que publica tem uma skill que o manda correr.

Achado do levantamento da F8 (`docs/handoff-v1/F8/RELATORIO.md`): `inventory.py` é o único
publicador de `_design/scope.json` e `_design/work-packages.json`, e nenhuma skill o
invocava. `/render` (7c) e `release.py` liam os dois ficheiros; numa sessão real nunca
existiriam, e nenhum pacote se construía. Os testes da F6 escreviam o inventário pelo
próprio teste, por isso nada ficava vermelho. A F6 §0 previa a autoria «na sessão,
`/blueprint` e `/render`»; o `/render` não pode inventar trabalho nem mudar âmbito, por isso
os dois passos entraram no `/blueprint` (15b e 17).

Limite declarado: estrutural. Prova que a instrução existe e que os comandos que nomeia
existem no motor; não prova que uma sessão a segue — é isso que os pilotos da F8 medem.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "library" / "kernel" / "tools"
TEXTOS = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
          for p in sorted(list((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
                          + list((ROOT / ".claude" / "commands").glob("*.md")))}
BLUEPRINT = TEXTOS[".claude/skills/aisa-blueprint/SKILL.md"]
FLAT = " ".join(BLUEPRINT.split())

# Os comandos que escrevem autoridade ou estado coordenado, por motor.
PUBLICADORES = {
    "inventory.py": ["draft", "check", "publish"],
    "functional.py": ["draft", "publish", "authorization-block", "approval-block"],
    "review.py": ["draft-candidates", "publish-candidates"],
    "release.py": ["build", "acceptance-block"],
    "resolve.py": ["draft", "publish"],
    "coverage.py": ["finalize"],
}


def escolhas(motor):
    texto = (TOOLS / motor).read_text(encoding="utf-8")
    fora = set()
    for bloco in re.findall(r'add_argument\(\s*"(?:command|cmd|action)"[^)]*choices=\[([^\]]*)\]',
                            texto):
        fora |= set(re.findall(r'"([a-z][a-z-]*)"', bloco))
    return fora


class CadaPublicadorTemQuemOChame(unittest.TestCase):

    def test_every_publishing_command_is_named_by_some_skill(self):
        orfaos = []
        for motor, comandos in PUBLICADORES.items():
            for c in comandos:
                alvo = "{} {}".format(motor, c)
                if not any(alvo in t for t in TEXTOS.values()):
                    orfaos.append(alvo)
        self.assertEqual(orfaos, [], "comandos que publicam sem skill que os mande correr")

    def test_both_inventory_kinds_are_authored(self):
        for kind in ("--kind scope", "--kind work-packages"):
            self.assertTrue(any("inventory.py" in t and kind in t for t in TEXTOS.values()),
                            kind)

    def test_the_inventory_commands_named_exist_in_the_motor(self):
        nomes = set(re.findall(r"inventory\.py ([a-z-]+)", "\n".join(TEXTOS.values())))
        self.assertTrue(nomes)
        self.assertEqual(nomes - escolhas("inventory.py"), set())


class OsPassosNoBlueprint(unittest.TestCase):

    def test_scope_sits_between_approval_and_authorisation_and_work_after(self):
        i15 = BLUEPRINT.index("15. **On approval**")
        i15b = BLUEPRINT.index("15b. **Scope of the delivery**")
        i16 = BLUEPRINT.index("16. **Authorising functional contracts**")
        i17 = BLUEPRINT.index("17. **Work inventory**")
        self.assertLess(i15, i15b)
        self.assertLess(i15b, i16)
        self.assertLess(i16, i17)
        self.assertLess(i17, BLUEPRINT.index("## Domain Knowledge pull rules"))

    def test_the_owner_authorises_the_scope_and_nothing_is_excluded_by_the_executor(self):
        s15b = " ".join(BLUEPRINT.split("15b. **Scope of the delivery**")[1]
                        .split("16. **Authorising")[0].split())
        self.assertIn("Ask the owner through `AskUserQuestion`", s15b)
        self.assertIn("Nothing is excluded on the executor's initiative", s15b)
        self.assertIn("never a scope authorised on the owner's behalf", s15b)
        self.assertIn("Skip in draft mode", s15b)

    def test_the_inventory_carries_no_effort_and_invents_no_work(self):
        s17 = " ".join(BLUEPRINT.split("17. **Work inventory**")[1]
                       .split("## Domain Knowledge")[0].split())
        self.assertIn("**No effort field**", s17)
        self.assertIn("never a WP invented to silence a finding", s17)
        self.assertIn("trace.py scope-gate", s17)

    def test_the_render_still_may_not_invent_work(self):
        render = TEXTOS[".claude/skills/aisa-render/SKILL.md"]
        self.assertIn("invent work", render.split("### What this skill MAY NOT do")[1][:400])
        self.assertNotIn("inventory.py", render)


if __name__ == "__main__":
    unittest.main(verbosity=1)
