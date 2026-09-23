"""pre-profile-check.py — PreToolUse guard for Skill: no write skill on a legacy engagement.

handoff-v1 F1.4 (decisão classic A). A versão nova não tem runtime classic: um engagement
sem bloco `workflow` em `_state.json` foi criado pela versão histórica e aqui só se lê.
O guarda de autoridade e o coordenador já recusam a escrita — mas recusam-na no momento
de escrever, depois de a skill ter começado. O `/capture`, por exemplo, escreveria os seus
derivados em `_capture/` antes de chegar ao `_state.json`. Este guarda recusa ANTES, na
invocação, para que um engagement legado fique exactamente como estava.

O QUE CONTA COMO SKILL QUE ESCREVE
    Todas as skills do aisa (`aisa-*`, `lens-*`, `chairman-synthesis`) menos as de leitura
    declaradas em LEITURA. Uma skill nova escreve até ser declarada de leitura: falha
    fechada. Skills fora do aisa não são deste guarda.

QUAL ENGAGEMENT
    O nomeado (`--engagement <slug>`) ou o único montado. Com vários montados e nenhum
    nomeado, adivinhar o mais recente e recusar por ele seria recusar pelo projecto errado:
    aí o guarda avisa e deixa passar, e as outras duas camadas continuam a recusar a
    escrita propriamente dita.

`AISA_GUARD_MODE=log` é o override administrativo explícito, como nos vizinhos.
"""

from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import arg_slug, find_engagement, tool_payload, utf8_stderr  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / "library" / "kernel" / "tools" / "workflow.py"

LEITURA = {"aisa-status", "aisa-orient", "aisa-start"}


def escreve(skill: str) -> bool:
    nome = skill.split(":")[-1]
    if nome in LEITURA:
        return False
    return nome.startswith(("aisa-", "lens-")) or nome == "chairman-synthesis"


def block(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}),
          file=sys.stderr)
    sys.exit(2)


def main() -> int:
    utf8_stderr()
    tool = tool_payload(sys.stdin.read())
    if tool.get("tool_name") != "Skill":
        return 0
    ti = tool.get("tool_input") or {}
    skill = ti.get("skill") or ""
    if not escreve(skill):
        return 0
    eng, how = find_engagement(arg_slug(ti.get("args") or ""), allow_ambiguous=False)
    if eng is None:
        if how == "ambiguous":
            print("[pre-profile-check] vários engagements montados e nenhum nomeado — o "
                  "perfil não foi verificado aqui; o guarda de autoridade e o coordenador "
                  "continuam a recusar escrita num engagement da versão histórica.",
                  file=sys.stderr)
        return 0
    W = runpy.run_path(str(WORKFLOW))
    if W["profile_of"](eng)["kind"] != W["LEGACY"]:
        return 0
    r = W["validate_profile"](eng)
    razao = "`{}` é um engagement da versão histórica: {} — {}".format(
        eng.name, " · ".join(x["detail"] for x in r["reasons"]),
        " · ".join(a["action"] for a in r["next_actions"]))
    if os.environ.get("AISA_GUARD_MODE") == "log":
        print("[pre-profile-check] (log) {} — `{}` permitido por override".format(razao, skill),
              file=sys.stderr)
        return 0
    block("{}\n\n`{}` escreve no engagement e não corre aqui. `AISA_GUARD_MODE=log` é o "
          "override administrativo explícito.".format(razao, skill))
    return 2


if __name__ == "__main__":
    sys.exit(main())
