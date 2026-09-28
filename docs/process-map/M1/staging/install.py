"""Instala o M1 do mapa de conhecimento do processo em `library/` — corre-o o mantenedor.

A guarda de `library/` (pre-write-guard + regras deny) impediu a sessão de desenvolvimento
de escrever lá; este script é o passo administrativo, fora do runtime, que o CLAUDE.md
sanciona («out-of-band administrative edits via git commit»). Não mexe em engagements.

    python docs/process-map/M1/staging/install.py            # aplica
    python docs/process-map/M1/staging/install.py --check    # só confere, não escreve

Faz, por esta ordem, e pára no primeiro problema:
  1. confirma que os três ficheiros a alterar em `library/` estão sem alterações locais;
  2. `git apply` dos patches (workflow.py SUPPORTED, orchestration.md, template §1);
  3. copia o motor e o schema para `library/kernel/tools/` e `library/kernel/schemas/`
     (recusa se já existirem com conteúdo diferente);
  4. regista `library/kernel/tools/process_map.py` no inventário F0
     (`docs/handoff-v1/F0/consumer-matrix.json`).
Depois: `python .github/run_tests.py`, rever `git diff`, commit.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PATCHES = ["workflow.patch", "orchestration.patch", "process-model.patch"]
TARGETS = ["library/kernel/tools/workflow.py", "library/kernel/orchestration.md",
           "library/kernel/capture-templates/process-model.template.md"]
COPIES = {HERE / "kernel" / "tools" / "process_map.py": ROOT / "library/kernel/tools/process_map.py",
          HERE / "kernel" / "schemas" / "process-map.schema.json":
              ROOT / "library/kernel/schemas/process-map.schema.json"}
MATRIX = ROOT / "docs/handoff-v1/F0/consumer-matrix.json"
MOTOR_REL = "library/kernel/tools/process_map.py"
ENTRIES = {
    "su": ("declares-contract", "Motor do mapa de conhecimento do processo: declara que o mapa "
           "organiza conhecimento e referências e que a SU continua a ser a autoridade dos factos; "
           "não lê nem escreve a SU no M1 (a coluna `elementos` chega no M3)."),
    "decisions": ("reader", "Lê os cabeçalhos `## D-NNN` de decisions.md para validar o "
                  "`decision_ref` de um órfão `out_of_scope` material; nunca escreve decisões."),
    "state": ("reader", "Resolve `--engagement` pelo `find_engagement` do coverage.py, que "
              "reconhece um engagement pelo `_state.json`; não lê nem escreve o estado."),
}


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True,
                          check=check)


def main(argv):
    only_check = "--check" in argv
    dirty = [t for t in TARGETS if git("status", "--porcelain", "--", t).stdout.strip()]
    if dirty:
        print("recusado: alterações locais em {}".format(", ".join(dirty)))
        return 2
    for p in PATCHES:
        r = git("apply", "--check", str(HERE / p), check=False)
        if r.returncode:
            print("recusado: {} não aplica: {}".format(p, r.stderr.strip()))
            return 2
    for src, dst in COPIES.items():
        if dst.exists() and dst.read_bytes() != src.read_bytes():
            print("recusado: {} já existe com outro conteúdo".format(dst.relative_to(ROOT)))
            return 2
    if only_check:
        print("ok: tudo aplica; nada foi escrito (--check)")
        return 0
    for p in PATCHES:
        git("apply", str(HERE / p))
    for src, dst in COPIES.items():
        shutil.copyfile(src, dst)
    m = json.loads(MATRIX.read_text(encoding="utf-8"))
    for key, (role, mech) in ENTRIES.items():
        cons = m["artifacts"][key]["consumers"]
        if not any(c["file"] == MOTOR_REL for c in cons):
            cons.append({"file": MOTOR_REL, "kind": "engine", "role": role, "mechanism": mech,
                         "via": "", "evidence": MOTOR_REL, "confidence": "verified",
                         "source": "inventory"})
    MATRIX.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("instalado: 3 patches, motor, schema, inventário F0. A seguir: "
          "python .github/run_tests.py && git diff --stat")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
