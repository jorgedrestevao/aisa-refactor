"""Validate this planning package, not the AISA implementation.

Usage: python3 validate_package.py [--zip /absolute/path/package.zip]
Only packages the explicitly listed planning files. Does not inspect credentials,
mutate an AISA repository or claim that implementation tests passed.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


FILES = [
    "README.md", "01_BASELINE.md", "02_CONTRATOS.md",
    "03_AGENTES_E_PACK.md", "04_CONTINUIDADE.md", "05_FASES.md",
    "06_VALIDACAO.md", "07_MIGRACAO.md", "08_HANDOFF.md",
    "09_DEPENDENCIAS_E_TESTES.md",
    "PROMPT_IMPLEMENTACAO.md", "templates/RELATORIO_FASE.md",
    "examples/functional-contract.json", "examples/work-checkpoint.json",
    "validate_package.py",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    contents = {}
    for name in FILES:
        path = root / name
        assert path.is_file(), f"Missing file: {name}"
        data = path.read_bytes()
        assert data, f"Empty file: {name}"
        contents[name] = data
        if path.suffix == ".json":
            parsed = json.loads(data)
            assert parsed["example_only"] is True
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", data.decode()):
                if "://" not in target and not target.startswith("#"):
                    assert (path.parent / target.split("#")[0]).is_file(), target

    validation = contents["06_VALIDACAO.md"].decode()
    ids = re.findall(r"^\| (T\d{2}) \|", validation, re.M)
    assert ids == [f"T{i:02}" for i in range(1, 47)], "Test registry mismatch"
    phases = contents["05_FASES.md"].decode()
    assert re.findall(r"^## (F\d+) —", phases, re.M) == [f"F{i}" for i in range(10)]
    for name, data in contents.items():
        if name.endswith(".md"):
            for test in re.findall(r"\bT\d{2}\b", data.decode()):
                assert test in ids, f"Unknown test reference {test} in {name}"

    manifest = {
        "package_version": "1.2",
        "baseline_commit": "85baf1018ca2b238c41745f7f13dbb539589867f",
        "implementation_tests_executed_by_this_validator": False,
        "checks": {"files": len(FILES), "phases": 10, "specified_tests": 46,
                   "relative_links": "valid", "json_examples": "parseable"},
        "sha256": {name: hashlib.sha256(data).hexdigest()
                   for name, data in contents.items()},
    }
    if args.zip:
        output = args.zip.resolve()
        assert output.suffix == ".zip", "Output must be a ZIP"
        assert not output.exists(), "Refusing to overwrite an existing package"
        with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in contents.items():
                archive.writestr(f"AISA_Refactor_Handoff/{name}", data)
            archive.writestr("AISA_Refactor_Handoff/MANIFEST.json",
                             json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        with zipfile.ZipFile(output) as archive:
            assert archive.testzip() is None, "ZIP integrity failure"
        manifest["zip_created"] = str(output)
    print(json.dumps(manifest["checks"], ensure_ascii=False))
    print("PASS: planning package checks only; no AISA runtime tests executed.")


if __name__ == "__main__":
    main()
