# -*- coding: utf-8 -*-
"""`_state.json` de um engagement `handoff-v1` para testes (sintetico).

Desde handoff-v1 F1.4, um `_state.json` sem bloco `workflow` e um engagement da versao
historica: o bootstrap nao fica pronto, o guarda recusa escrever e o coordenador recusa
publicar (decisao classic A). As fixtures que exercitam os motores sobre um engagement
normal usam este estado; as que testam o legado escrevem o `_state.json` sem o bloco.

    ESTADO = runpy.run_path(str(ROOT / ".claude" / "tests" / "fixtures" / "handoff-v1"
                                / "estado.py"))["estado"]
    (eng / "_state.json").write_text(ESTADO(phase="discovery", round="R-01"), ...)
"""
import copy
import json

BLOCO = {"profile": "handoff-v1", "schema_version": "handoff-state/1",
         "route": "solution-choice", "route_revision": 1,
         "route_basis": {"justification": "plataforma em aberto (fixture sintetica)",
                         "source_refs": [], "authority_ref": None},
         "route_history": []}


def estado(**campos) -> str:
    """Uma linha JSON: `pack = pp`, bloco `workflow` valido, mais os campos dados."""
    base = {"pack": "pp", "workflow": copy.deepcopy(BLOCO)}
    base.update(campos)
    return json.dumps(base, ensure_ascii=False) + "\n"
