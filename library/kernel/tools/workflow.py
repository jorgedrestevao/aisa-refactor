# -*- coding: utf-8 -*-
"""Perfil de workflow `handoff-v1` — identificacao, capacidades do pack e respostas (F1).

    python library/kernel/tools/workflow.py check --engagement <slug> [--json]
    python library/kernel/tools/workflow.py check --pack <id> --profile handoff-v1 --route <rota> [--json]
    python library/kernel/tools/workflow.py task plan|start|receive|reconcile|show ... --engagement <slug>
    python library/kernel/tools/workflow.py resume --engagement <slug> [--budget N] [--json]

Stdlib apenas (ADR-001). `check` nao escreve nada; `task` escreve so o checkpoint
(`_work/checkpoint.json`), e so pelo coordenador.

O QUE E
    O ponto unico onde se responde a tres perguntas antes de escrever num engagement:
    que perfil tem, se o pack o suporta, e se o bloco `workflow` de `_state.json` e valido.
    Hooks, skills e o coordenador perguntam aqui, e so aqui (desenho F1, I-06).

O QUE NAO E
    Nao e um motor novo de estado: nao reconstroi e nao decide conteudo. O checkpoint e
    calculado aqui e publicado por `operation.run`, como qualquer autoridade (F2.3). A
    publicacao continua em `operation.py`, a reconstrucao em `bootstrap.py`, o espelho em
    `graph.py`/`resolve.py` e a frescura semantica em `coverage.py`.

LEGADO NAO E `LEGACY_MODE`
    Um engagement sem bloco `workflow` e legado do plano handoff-v1: foi criado pela versao
    historica (`jorgedrestevao/aisa@85baf10`) e nesta versao so se le (decisao classic A).
    `LEGACY_MODE`, no bootstrap, quer dizer outra coisa — engagement sem `_graph/` — e nao
    se reutiliza.

CAMPOS DESCONHECIDOS
    O validador de schema reporta campos que o schema nao declara e nunca os apaga. Quem le
    um bloco com campos a mais preserva-os; quem os deita fora esta a perder dados.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import runpy
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
# O leitor de YAML do kernel vive no dashboard (subconjunto Y1-Y7). Carrega-se so quando
# um `pack.yaml` e lido: o coordenador pergunta o perfil em cada publicacao e nao deve
# pagar o dashboard inteiro por isso.
_CACHE: dict = {}


def _dash() -> dict:
    if "D" not in _CACHE:
        _CACHE["D"] = runpy.run_path(str(_HERE / "dashboard.py"))
    return _CACHE["D"]

PROFILE = "handoff-v1"
STATE_SCHEMA = "handoff-state/1"
ROUTES = ("solution-choice", "platform-constrained", "change-impact")
# `change-impact` entra por reabertura sobre baseline aprovada, nunca no nascimento.
BIRTH_ROUTES = ("solution-choice", "platform-constrained")
HISTORICAL_VERSION = "jorgedrestevao/aisa@85baf10"

UNSUPPORTED_PROFILE = "UNSUPPORTED_PROFILE"
STALE_INPUT = "STALE_INPUT"
INCOMPLETE_READ_SET = "INCOMPLETE_READ_SET"
AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
INTEGRITY_FAILURE = "INTEGRITY_FAILURE"
SCHEMA_UNSUPPORTED = "SCHEMA_UNSUPPORTED"
BLOCKING_GAP = "BLOCKING_GAP"
RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
CODES = (UNSUPPORTED_PROFILE, STALE_INPUT, INCOMPLETE_READ_SET, AUTHORIZATION_REQUIRED,
         INTEGRITY_FAILURE, SCHEMA_UNSUPPORTED, BLOCKING_GAP, RECOVERY_REQUIRED)

# F7 (Q4): a tabela ÚNICA do que esta versão lê, por artefacto. Um leitor que encontra outra
# versão (futura, ou sem `schema_version`) recusa com `SCHEMA_UNSUPPORTED` e não toca no
# ficheiro — nunca lê à sorte nem trunca campos que não conhece (T36). A ordem conta: o
# primeiro padrão que casa decide (o mandato antes do parecer). Os rascunhos (`_drafts/`)
# não são artefactos publicados e não entram.
SUPPORTED = (
    ("_state.json#workflow", "handoff-state/1"),
    ("_work/checkpoint.json", "handoff-work/1"),
    ("_design/functional-contracts.json", "handoff-functional/1"),
    ("_design/scope.json", "handoff-scope/1"),
    ("_design/work-packages.json", "handoff-work-packages/1"),
    ("_design/candidates.json", "handoff-candidates/1"),
    ("_design/reviews/ledger.json", "aisa-review-ledger/1"),
    ("_design/reviews/REV-*.mandate.json", "aisa-review-mandate/1"),
    ("_design/reviews/REV-*.json", "handoff-review/1"),
    ("_release/r*/handoff-index.json", "handoff-index/1"),
    # process-map M1: o mapa de conhecimento do processo e o seu histórico imutável.
    ("_map/map.json", "process-map/1"),
    ("_map/history/mp-v*.json", "process-map/1"),
)


def supported_schema(path) -> str:
    """A versão que esta versão do código lê para `path` (relativo ao engagement, ou absoluto:
    casa pelo fim do caminho); vazio quando o caminho não é um artefacto versionado."""
    import fnmatch
    s = str(path).replace(os.sep, "/")
    for pat, schema in SUPPORTED:
        if fnmatch.fnmatchcase(s, pat) or fnmatch.fnmatchcase(s, "*/" + pat):
            return schema
    return ""


def schema_problem(path, data) -> str:
    """Vazio se `data` é da versão suportada para `path`; senão a razão, pronta a dizer."""
    want = supported_schema(path)
    if not want or not isinstance(data, dict):
        return ""
    got = data.get("schema_version")
    if got == want:
        return ""
    return "`{}` tem schema `{}`; esta versão lê `{}` — nada se lê nem escreve por " \
           "cima".format(Path(str(path)).name, got, want)


class SchemaError(Exception):
    """Recusa de versão para os leitores só-de-leitura (`impact`, `trace`)."""

    def __init__(self, message: str, path: str = ""):
        super().__init__(message)
        self.code = SCHEMA_UNSUPPORTED
        self.detail = {"path": path}

# O que `profile_of` devolve em `kind`.
HANDOFF = "handoff"
LEGACY = "legacy"
UNBORN = "unborn"
UNREADABLE = "unreadable"

SCHEMAS_DIR = _HERE.parent / "schemas"
PACKS_DIR = _HERE.parent.parent / "packs"


# ------------------------------------------------------------------ resposta

def response(ok, code=None, reasons=(), affected_ids=(), input_revision=None,
             next_actions=()) -> dict:
    """O envelope de 02 §9. `ok=True` nunca traz codigo; `ok=False` traz sempre um estavel."""
    if ok and code is not None:
        raise ValueError("resposta ok nao traz codigo")
    if not ok and code not in CODES:
        raise ValueError("codigo nao estavel: {!r}".format(code))
    return {"ok": bool(ok), "code": code,
            "reasons": [dict(r) for r in reasons],
            "affected_ids": list(affected_ids),
            "input_revision": input_revision,
            "next_actions": [dict(a) for a in next_actions]}


def _reason(detail, source="workflow", source_code=None):
    r = {"detail": detail, "source": source}
    if source_code:
        r["source_code"] = source_code
    return r


# ------------------------------------------------------------------ schemas

def load_schema(name: str) -> dict:
    """`handoff-state` -> o schema versionado em `library/kernel/schemas/`."""
    return json.loads((SCHEMAS_DIR / (name + ".schema.json")).read_text(encoding="utf-8"))


_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _is_type(value, name):
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[name])


def validate(instance, schema: dict, root: dict | None = None, path: str = "$"):
    """`(erros, desconhecidos)` — o subconjunto de JSON Schema que os schemas usam.

    Palavras-chave: `type`, `const`, `enum`, `required`, `properties`, `items`,
    `minItems`, `minLength`, `minimum`, `pattern`, `$ref` local e `additionalProperties`
    como schema (os valores de um mapa: cada chave vale contra ele e nao e desconhecida).
    Qualquer outra num schema
    e erro de schema, nao silencio. `desconhecidos` lista os campos que o schema nao
    declara: sao reportados e preservados, nunca apagados."""
    root = root or schema
    errors, unknown = [], []
    known = {"$schema", "$id", "title", "description", "$defs", "type", "const", "enum",
             "required", "properties", "items", "minItems", "minLength", "minimum",
             "pattern", "$ref", "additionalProperties"}
    extra = set(schema) - known
    if extra:
        return ["{}: palavra-chave de schema fora do subconjunto: {}".format(
            path, ", ".join(sorted(extra)))], unknown
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            return ["{}: $ref nao local: {}".format(path, ref)], unknown
        return validate(instance, root["$defs"][ref.split("/")[-1]], root, path)
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(instance, n) for n in names):
            return ["{}: tipo {} esperado".format(path, "|".join(names))], unknown
    if "const" in schema and instance != schema["const"]:
        errors.append("{}: valor {!r} != {!r}".format(path, instance, schema["const"]))
    if "enum" in schema and instance not in schema["enum"]:
        errors.append("{}: valor {!r} fora de {}".format(path, instance, schema["enum"]))
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append("{}: texto vazio".format(path))
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append("{}: {!r} nao segue {}".format(path, instance, schema["pattern"]))
    if _is_type(instance, "number") and "minimum" in schema and instance < schema["minimum"]:
        errors.append("{}: {} < {}".format(path, instance, schema["minimum"]))
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append("{}: menos de {} item(ns)".format(path, schema["minItems"]))
        if "items" in schema:
            for i, item in enumerate(instance):
                e, u = validate(item, schema["items"], root, "{}[{}]".format(path, i))
                errors += e
                unknown += u
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append("{}: falta `{}`".format(path, key))
        props = schema.get("properties")
        extra = schema.get("additionalProperties")
        if extra is not None and not isinstance(extra, dict):
            return errors + ["{}: additionalProperties so como schema".format(path)], unknown
        if props is not None or extra is not None:
            for key, value in instance.items():
                sub = "{}.{}".format(path, key)
                if props is not None and key in props:
                    e, u = validate(value, props[key], root, sub)
                elif extra is not None:
                    e, u = validate(value, extra, root, sub)
                else:
                    e, u = [], [sub]
                errors += e
                unknown += u
    return errors, unknown


# ------------------------------------------------------------------ perfil

def _read_state(eng: Path):
    p = Path(eng) / "_state.json"
    if not p.is_file():
        return None, None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, "{}: {}".format(type(exc).__name__, exc)
    if not isinstance(data, dict):
        return None, "o conteudo nao e um objecto JSON"
    return data, None


def profile_of(eng) -> dict:
    """Que perfil tem o engagement. Le `_state.json` e nada mais.

    `kind`:
      `unborn`     sem `_state.json` — o `/start` esta a cria-lo;
      `unreadable` `_state.json` existe e nao se le — nunca se trata como legado;
      `legacy`     `_state.json` sem bloco `workflow` — versao historica, so leitura aqui;
      `handoff`    bloco `workflow` presente (a validade verifica-se em `validate_profile`).
    """
    state, err = _read_state(eng)
    if err:
        return {"kind": UNREADABLE, "workflow": None, "state": None, "detail": err}
    if state is None:
        return {"kind": UNBORN, "workflow": None, "state": None, "detail": ""}
    if "workflow" not in state:
        return {"kind": LEGACY, "workflow": None, "state": state,
                "detail": "sem bloco `workflow`: engagement da versao historica"}
    return {"kind": HANDOFF, "workflow": state["workflow"], "state": state, "detail": ""}


# ------------------------------------------------------------ escrita de autoridades

def state_problems(actual_text: str, new_text: str) -> list:
    """Razoes para recusar `new_text` como `_state.json` sobre `actual_text` (F1 I-07).

    Nenhuma chave existente desaparece em silencio, e o bloco `workflow` nao muda por
    esta via: muda-o o `workflow.py` pelo coordenador. Um `_state.json` actual que nao se
    le nao tem nada a comparar — quem decide e o bootstrap. Uma regra, dois consumidores:
    o guarda (escrita por ferramenta) e `resolve.publish` (escrita pelo coordenador)."""
    try:
        actual = json.loads(actual_text)
    except (TypeError, ValueError):
        return []
    if not isinstance(actual, dict):
        return []
    try:
        novo = json.loads(new_text)
    except ValueError as exc:
        return [_reason("o `_state.json` novo não é JSON ({})".format(exc),
                        source_code="STATE_NOT_JSON")]
    if not isinstance(novo, dict):
        return [_reason("o `_state.json` novo não é um objecto JSON",
                        source_code="STATE_NOT_JSON")]
    fora = []
    perdidas = sorted(set(actual) - set(novo))
    if perdidas:
        fora.append(_reason(
            "o `_state.json` novo deixa cair {} — campos existentes não se descartam em "
            "silêncio".format(", ".join("`{}`".format(k) for k in perdidas)),
            source_code="STATE_KEYS_DROPPED"))
    if "workflow" in actual and novo.get("workflow") != actual.get("workflow"):
        fora.append(_reason(
            "o bloco `workflow` (perfil e rota) não muda por esta via: muda-o o "
            "`workflow.py` pelo coordenador", source_code="WORKFLOW_CHANGED"))
    return fora


def su_problems(eng, old_text: str, new_text: str, overlay: dict | None = None) -> list:
    """Razoes para recusar `new_text` como SU de um engagement `handoff-v1` (T08, F0 D19).

    1. Nenhuma linha desaparece: a SU e append-only; uma transicao acrescenta a sucessora e
       as edicoes sancionadas mudam celulas, nunca apagam a linha.
    2. Uma linha `Confirmed` nova, ou existente que a escrita muda (promocao no lugar com o
       mesmo id incluida), traz um localizador das classes de `states.md` → *Confirmed
       threshold*, com o alvo presente. Verificador do motor (`audit_confirmed_locators`),
       o mesmo que o `/status` le: presenca e existencia do alvo, nunca a verdade.
       `overlay` sao os outros ficheiros publicados na MESMA operacao: um alvo que nasce
       com a linha que o cita conta (`dashboard.evidence_targets`)."""
    D = _dash()
    velhas = {r["id"]: (r["state"], r["raw"]) for r in D["parse_su"](old_text or "")[1]}
    linhas = D["parse_su"](new_text)[1]
    fora = []
    sumidas = sorted(set(velhas) - {r["id"] for r in linhas})
    if sumidas:
        fora.append(_reason(
            "linha(s) apagada(s) da SU: {} — a SU é append-only; uma transição acrescenta a "
            "sucessora (`was <id>`)".format(", ".join(sumidas)),
            source_code="SU_ROW_REMOVED"))
    tocadas = {r["id"] for r in linhas
               if r["state"] == "Confirmed" and not r["resolved"]
               and velhas.get(r["id"]) != (r["state"], r["raw"])}
    if tocadas:
        audit = D["audit_confirmed_locators"](linhas, Path(eng), only_ids=tocadas,
                                              overlay=overlay)
        falhas = ["{} ({})".format(x["id"], x["motivo"])
                  for x in audit["sem_locator"] + audit["alvo_ausente"]]
        if falhas:
            fora.append(_reason(
                "linha(s) `Confirmed` sem prova localizável: {} — concordância entre "
                "personas não é evidência (`library/kernel/states.md` → *Confirmed "
                "threshold*); escrever como `Assumed` com a base, ou `Unknown`".format(
                    "; ".join(falhas)), source_code="CONFIRMED_WITHOUT_LOCATOR"))
    return fora


def pack_capabilities(pack: str, packs_dir: Path | None = None) -> dict:
    """As capacidades que `pack.yaml` DECLARA. O que nao esta declarado nao e suportado."""
    p = Path(packs_dir or PACKS_DIR) / (pack or "") / "pack.yaml"
    if not pack or not p.is_file():
        return {"pack": pack, "found": False, "declared": False, "capabilities": {},
                "errors": ["pack.yaml de `{}` nao existe".format(pack)], "unknown": []}
    text = p.read_text(encoding="utf-8")
    caps = {}
    for key in ("supported_workflow_profiles", "supported_routes", "design_contract_version"):
        val = _dash()["yl_scalar_at"](text, key)
        if val is not None:
            caps[key] = val
    if not caps:
        return {"pack": pack, "found": True, "declared": False, "capabilities": {},
                "errors": [], "unknown": []}
    errors, unknown = validate(caps, load_schema("handoff-pack"))
    return {"pack": pack, "found": True, "declared": not errors, "capabilities": caps,
            "errors": errors, "unknown": unknown}


def _legacy_refusal() -> dict:
    return response(False, UNSUPPORTED_PROFILE,
                    [_reason("engagement sem perfil persistido (legado): esta versao so o le",
                             source_code="legacy_profile_absent")],
                    next_actions=[
                        {"action": "ler o engagement aqui (/status, /dashboard, /resume)",
                         "reason": "a leitura nao altera nada"},
                        {"action": "continuar o trabalho em {}".format(HISTORICAL_VERSION),
                         "reason": "a versao nova nao tem runtime classic (decisao A)"}])


def _check_request(pack, profile, route, packs_dir=None) -> dict:
    if profile != PROFILE:
        return response(False, UNSUPPORTED_PROFILE,
                        [_reason("perfil `{}` nao existe nesta versao".format(profile))],
                        next_actions=[{"action": "usar o perfil {}".format(PROFILE),
                                       "reason": "unico perfil desta versao"}])
    caps = pack_capabilities(pack, packs_dir)
    if not caps["found"]:
        return response(False, UNSUPPORTED_PROFILE, [_reason(e) for e in caps["errors"]])
    if caps["errors"]:
        return response(False, UNSUPPORTED_PROFILE,
                        [_reason("declaracao de capacidades invalida: " + e) for e in caps["errors"]])
    declared = caps["capabilities"]
    if not caps["declared"] or profile not in declared.get("supported_workflow_profiles", []):
        return response(False, UNSUPPORTED_PROFILE,
                        [_reason("o pack `{}` nao declara o perfil {}".format(pack, profile))],
                        next_actions=[{"action": "escolher um pack que declare {}".format(profile),
                                       "reason": "sem declaracao nao ha fallback"}])
    if route not in declared.get("supported_routes", []):
        return response(False, UNSUPPORTED_PROFILE,
                        [_reason("o pack `{}` nao declara a rota `{}`".format(pack, route))])
    return response(True)


def validate_profile(eng=None, *, pack=None, profile=None, route=None,
                     birth=False, packs_dir=None) -> dict:
    """Pode este engagement (ou este pedido de criacao) seguir no perfil `handoff-v1`?

    Com `eng`: le `_state.json`, identifica o legado e valida o bloco `workflow` contra o
    schema e contra o que o pack declara. Com `pack`/`profile`/`route` e sem engagement:
    valida um pedido de criacao (`birth=True` admite so as rotas de nascimento)."""
    if eng is None:
        if birth and route not in BIRTH_ROUTES:
            return response(False, UNSUPPORTED_PROFILE,
                            [_reason("a rota `{}` nao se escolhe no nascimento".format(route))],
                            next_actions=[{"action": "escolher uma de: " + ", ".join(BIRTH_ROUTES),
                                           "reason": "change-impact exige baseline aprovada"}])
        return _check_request(pack, profile, route, packs_dir)

    eng = Path(eng)
    who = profile_of(eng)
    if who["kind"] == UNBORN:
        return response(False, INTEGRITY_FAILURE,
                        [_reason("`{}` nao tem `_state.json`".format(eng.name))])
    if who["kind"] == UNREADABLE:
        return response(False, INTEGRITY_FAILURE,
                        [_reason("`_state.json` ilegivel: " + who["detail"])])
    if who["kind"] == LEGACY:
        return _legacy_refusal()

    wf = who["workflow"]
    if isinstance(wf, dict) and wf.get("schema_version") not in (None, STATE_SCHEMA):
        return response(False, SCHEMA_UNSUPPORTED,
                        [_reason("bloco `workflow` com schema `{}`; esta versao le {}".format(
                            wf.get("schema_version"), STATE_SCHEMA))],
                        next_actions=[{"action": "abrir com uma versao que leia esse schema",
                                       "reason": "nao se interpreta um schema por aproximacao"}])
    errors, _unknown = validate(wf, load_schema("handoff-state"))
    if errors:
        return response(False, INTEGRITY_FAILURE, [_reason(e) for e in errors])
    if wf["route"] == "platform-constrained" and not wf["route_basis"]["authority_ref"]:
        return response(False, INTEGRITY_FAILURE,
                        [_reason("rota platform-constrained sem `authority_ref` para a imposicao")])
    return _check_request(who["state"].get("pack"), wf["profile"], wf["route"], packs_dir)


# ------------------------------------------------------------ checkpoint e tarefas (F2.3)
#
# `_work/checkpoint.json` (`handoff-work/1`): o trabalho do proprio aisa, por referencias.
# Nunca copia a SU, as decisoes ou o blueprint — guarda ids, caminhos e hashes. Quem o
# publica e o coordenador (`operation.run`), como a qualquer autoridade: base esperada,
# recibo, recuperacao. Este modulo so calcula o conteudo novo.
#
# Estados (handoff-contract.md → *Checkpoint*): tarefa `planned` · `running` · `blocked` ·
# `completed` · `cancelled`; resultado `draft` · `received` · `integrated` · `superseded`,
# com frescura `current` · `stale` · `unverified`. `completed` so com resultado integrado.
# Depois de uma falha, `running` nao quer dizer que continua a correr: `reconcile` converte.

CHECKPOINT = "_work/checkpoint.json"
WORK_SCHEMA = "handoff-work/1"
TASK_RE = re.compile(r"^TASK-(\d{3,})$")


class WorkflowError(Exception):
    def __init__(self, message: str, code: str, detail: dict | None = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or {}

    def as_dict(self) -> dict:
        return {"error": str(self), "code": self.code, "detail": self.detail}


def _op() -> dict:
    if "O" not in _CACHE:
        _CACHE["O"] = runpy.run_path(str(_HERE / "operation.py"))
    return _CACHE["O"]


def _digest(p: Path) -> str:
    return _op()["digest"](p)


def read_checkpoint(eng) -> dict:
    """`{data, digest, unknown}` — `data` None quando ainda nao existe (ausencia e estado).

    Um checkpoint que existe e nao se le, ou que o schema recusa, NAO e ausencia: sobe como
    `INTEGRITY_FAILURE`, e ninguem escreve por cima dele. Campos que o schema nao declara
    sao reportados em `unknown` e preservados."""
    p = Path(eng) / CHECKPOINT
    dg = _digest(p)
    if not dg:
        return {"data": None, "digest": "", "unknown": []}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise WorkflowError("checkpoint ilegivel — nada se escreve por cima", INTEGRITY_FAILURE,
                            {"path": CHECKPOINT, "detail": str(exc)})
    if isinstance(data, dict) and data.get("schema_version") not in (None, WORK_SCHEMA):
        raise WorkflowError("checkpoint com schema `{}`; esta versao le {}".format(
            data.get("schema_version"), WORK_SCHEMA), SCHEMA_UNSUPPORTED,
            {"path": CHECKPOINT})
    errors, unknown = validate(data, load_schema("handoff-work"))
    if errors:
        raise WorkflowError("checkpoint invalido — nada se escreve por cima", INTEGRITY_FAILURE,
                            {"path": CHECKPOINT, "errors": errors})
    return {"data": data, "digest": dg, "unknown": unknown}


def _decision_ids(eng: Path) -> list:
    try:
        texto = (eng / "decisions.md").read_text(encoding="utf-8")
    except OSError:
        return []
    return sorted(set(re.findall(r"(?m)^#{1,4}\s*\**\s*(D-\d+)\b", texto)))


def new_checkpoint(eng) -> dict:
    """O checkpoint de partida, so com referencias: o objectivo e o pedido literal
    (`context.json#literal_request`), o ambito e o enquadramento declarado, as
    autorizacoes sao os blocos `D-` que existem. Nada e resumido nem copiado."""
    eng = Path(eng)
    who = profile_of(eng)
    if who["kind"] != HANDOFF:
        raise WorkflowError("checkpoint so num engagement handoff-v1", UNSUPPORTED_PROFILE,
                            {"kind": who["kind"]})
    wf = who["workflow"] or {}
    return {"schema_version": WORK_SCHEMA, "engagement_id": eng.name, "revision": 0,
            "profile": PROFILE, "route": wf.get("route"),
            "objective": "context.json#literal_request",
            "scope_refs": ["enquadramento.md"] if (eng / "enquadramento.md").is_file() else [],
            "authorization_refs": _decision_ids(eng),
            "last_integrated_operation": None, "active_task": None,
            "tasks": [], "results": [], "next_actions": []}


def next_actions(cp: dict) -> list:
    """Derivadas, nunca escritas a mao: o que esta pronto e porque e seguro."""
    por_id = {t["id"]: t for t in cp.get("tasks", [])}
    fora = []
    for r in cp.get("results", []):
        if r["status"] == "received":
            fora.append({"action": "resolve.py publish --draft {}".format(
                r["ref"].rsplit("/", 1)[-1]),
                "reason": "resultado {} de {} recebido e por integrar ({})".format(
                    r["id"], r["task_id"], r["freshness"])})
    for t in cp.get("tasks", []):
        deps = [por_id.get(d, {}).get("state") for d in t.get("dependencies", [])]
        if t["state"] == "planned" and all(s == "completed" for s in deps):
            fora.append({"action": "workflow.py task start {}".format(t["id"]),
                         "reason": "planeada; dependencias concluidas"})
        elif t["state"] == "blocked":
            fora.append({"action": "resolver o bloqueio de {}".format(t["id"]),
                         "reason": ", ".join(t.get("blocker_refs") or []) or "bloqueada"})
    return fora


def _render(cp: dict) -> str:
    cp = dict(cp, revision=int(cp.get("revision") or 0) + 1)
    running = [t["id"] for t in cp["tasks"] if t["state"] == "running"]
    cp["active_task"] = running[0] if running else None
    cp["next_actions"] = next_actions(cp)
    errors, _u = validate(cp, load_schema("handoff-work"))
    if errors:
        raise WorkflowError("checkpoint novo invalido — nao se publica", INTEGRITY_FAILURE,
                            {"errors": errors})
    return json.dumps(cp, ensure_ascii=False, indent=1) + "\n"


def _publish(eng: Path, prefixo: str, cp_atual: dict, cp_novo: dict,
             read_set: dict | None = None) -> dict:
    texto = _render(cp_novo)
    op_id = "{}-{}".format(prefixo, hashlib.sha256(
        (cp_atual["digest"] + texto).encode("utf-8")).hexdigest()[:16])
    recibo = _op()["run"](eng, op_id, {CHECKPOINT: texto},
                          expected={CHECKPOINT: cp_atual["digest"]}, read_set=read_set)
    return {"operation_id": op_id, "receipt": recibo, "checkpoint": json.loads(texto)}


def _task(cp: dict, task_id: str) -> dict:
    for t in cp.get("tasks", []):
        if t["id"] == task_id:
            return t
    raise WorkflowError("tarefa inexistente: {}".format(task_id), INTEGRITY_FAILURE,
                        {"task": task_id})


def _atual(eng: Path) -> tuple:
    cp = read_checkpoint(eng)
    data = cp["data"] if cp["data"] is not None else new_checkpoint(eng)
    return cp, json.loads(json.dumps(data))


def task_plan(eng, role, criteria, inputs=(), depends=()) -> dict:
    """Uma tarefa `planned`, com o proximo `TASK-NNN` — um id nunca e reutilizado: as
    tarefas nao se apagam, canceladas incluidas, e o maximo so cresce."""
    eng = Path(eng)
    crit = [c for c in (criteria or []) if str(c).strip()]
    if not crit:
        raise WorkflowError("tarefa sem criterio de fecho", INTEGRITY_FAILURE, {})
    cp, data = _atual(eng)
    for d in depends or ():
        _task(data, d)
    n = max([int(TASK_RE.match(t["id"]).group(1)) for t in data["tasks"]] or [0]) + 1
    tid = "TASK-{:03d}".format(n)
    data["tasks"].append({"id": tid, "role": role, "state": "planned",
                          "input_refs": [{"ref": str(r)} for r in inputs or ()],
                          "dependencies": list(depends or ()), "blocker_refs": [],
                          "completion_criteria": crit, "output_refs": []})
    out = _publish(eng, "task-plan", cp, data)
    return dict(out, task=tid)


def task_start(eng, task_id) -> dict:
    """`running`, e os inputs ganham o sha256 dos bytes que a tarefa vai consumir: a
    revisao consumida. Se mudarem ate a integracao, a integracao da `STALE_INPUT`."""
    eng = Path(eng)
    cp, data = _atual(eng)
    t = _task(data, task_id)
    if t["state"] not in ("planned", "blocked"):
        raise WorkflowError("{} esta `{}` — so arranca de planned ou blocked".format(
            task_id, t["state"]), INTEGRITY_FAILURE, {"task": task_id})
    por_id = {x["id"]: x for x in data["tasks"]}
    pendentes = [d for d in t["dependencies"] if por_id[d]["state"] != "completed"]
    if pendentes:
        raise WorkflowError("{} depende de tarefas por concluir: {}".format(
            task_id, ", ".join(pendentes)), BLOCKING_GAP, {"task": task_id})
    for ref in t["input_refs"]:
        ref["sha256"] = _digest(eng / ref["ref"]) or ("0" * 64)
    t["state"], t["blocker_refs"] = "running", []
    return _publish(eng, "task-start", cp, data)


def _input_revision(t: dict) -> str:
    corpo = json.dumps({r["ref"]: r.get("sha256", "") for r in t["input_refs"]},
                       sort_keys=True)
    return hashlib.sha256(corpo.encode("utf-8")).hexdigest()


def _freshness(eng: Path, t: dict) -> tuple:
    mudados = [r["ref"] for r in t["input_refs"]
               if (r.get("sha256") or "") != (_digest(eng / r["ref"]) or "0" * 64)]
    return ("stale" if mudados else "current"), mudados


def _resolve() -> dict:
    if "R" not in _CACHE:
        _CACHE["R"] = runpy.run_path(str(_HERE / "resolve.py"))
    return _CACHE["R"]


def task_receive(eng, task_id, draft_id) -> dict:
    """O resultado chega: `received`, nunca `integrated`. Nao entra na SU nem no grafo, e
    por isso nao conta para prontidao nem gates (T15); a retoma mostra-o. Um rascunho que
    cita o que nao declarou ter lido e recusado aqui (T10)."""
    eng = Path(eng)
    R = _resolve()
    m = R["read_draft"](eng, draft_id)
    if m.get("task") != task_id:
        raise WorkflowError("o rascunho {} nao serve {}".format(draft_id, task_id),
                            INTEGRITY_FAILURE, {"draft": draft_id, "task": task_id})
    d = R["draft_dir"](eng, draft_id)
    novos = {rel: (d / rel).read_text(encoding="utf-8") for rel, base in m["files"].items()
             if (d / rel).is_file() and _digest(d / rel) != base}
    lacunas = R["read_set_gaps"](eng, m, novos)
    if lacunas:
        raise WorkflowError("o resultado cita o que nao declarou ter lido", INCOMPLETE_READ_SET,
                            {"missing": lacunas, "draft": draft_id})
    cp, data = _atual(eng)
    t = _task(data, task_id)
    if t["state"] != "running":
        raise WorkflowError("{} esta `{}` — so recebe resultado quando running".format(
            task_id, t["state"]), INTEGRITY_FAILURE, {"task": task_id})
    frescura, mudados = _freshness(eng, t)
    base_mudada = [rel for rel, dg in list(m["files"].items()) + list(m["reads"].items())
                   if _digest(eng / rel) != dg]
    if base_mudada:
        frescura = "stale"
    sha = R["draft_digest"](eng, draft_id)
    for r in data["results"]:
        if r["task_id"] == task_id and r["status"] == "received":
            if r.get("sha256") == sha:
                return {"operation_id": None, "receipt": None, "checkpoint": data,
                        "result": r["id"], "replayed": True}
            r["status"] = "superseded"
            r["reason_not_integrated"] = "substituido por um resultado mais recente"
    rid = "RES-{:03d}".format(len(data["results"]) + 1)
    data["results"].append({
        "id": rid, "task_id": task_id, "status": "received", "freshness": frescura,
        "ref": "{}/{}".format(R["DRAFTS_DIR"], draft_id), "input_revision": _input_revision(t),
        "sha256": sha,
        "reason_not_integrated": ("por publicar" if frescura == "current" else
                                  "inputs mudaram desde o inicio da tarefa: {}".format(
                                      ", ".join(mudados + base_mudada)))})
    out = _publish(eng, "task-receive", cp, data)
    return dict(out, result=rid, freshness=frescura)


def integrate(eng, cp: dict, task_id, draft_id, op_id, sha) -> tuple:
    """`(texto do checkpoint novo, inputs consumidos)` — o delta que `resolve.publish` poe
    na MESMA operacao que as autoridades. Resultado `integrated`, tarefa `completed`,
    `last_integrated_operation`. So de uma tarefa `running` ou `blocked` a espera de
    integracao; os inputs consumidos voltam para o read-set da publicacao."""
    eng = Path(eng)
    data = json.loads(json.dumps(cp["data"] if cp["data"] is not None
                                 else new_checkpoint(eng)))
    t = _task(data, task_id)
    if t["state"] not in ("running", "blocked"):
        raise WorkflowError("{} esta `{}` — nao ha o que integrar".format(task_id, t["state"]),
                            INTEGRITY_FAILURE, {"task": task_id})
    ref = "{}/{}".format(_resolve()["DRAFTS_DIR"], draft_id)
    alvo = None
    for r in data["results"]:
        if r["task_id"] == task_id and r["status"] == "received":
            if r["ref"] == ref:
                alvo = r
            else:
                r["status"] = "superseded"
    if alvo is None:
        alvo = {"id": "RES-{:03d}".format(len(data["results"]) + 1), "task_id": task_id,
                "ref": ref, "input_revision": _input_revision(t)}
        data["results"].append(alvo)
    alvo.update({"status": "integrated", "freshness": "current", "sha256": sha})
    alvo.pop("reason_not_integrated", None)
    t["state"], t["blocker_refs"] = "completed", []
    t["output_refs"] = sorted(set(t.get("output_refs") or []) | {op_id})
    data["last_integrated_operation"] = op_id
    data["authorization_refs"] = sorted(set(data.get("authorization_refs") or [])
                                        | set(_decision_ids(eng)))
    consumidos = {r["ref"]: r["sha256"] for r in t["input_refs"]
                  if r.get("sha256") and r["sha256"] != "0" * 64}
    return _render(data), consumidos


def tasks_reconcile(eng) -> dict:
    """Depois de uma falha: nenhuma tarefa fica `running` sem prova de que corre.

    Com um resultado recebido → `blocked` a espera de integracao (o trabalho esta feito e
    guardado; falta publicar). Sem resultado → volta a `planned`, retomavel. Nunca relanca
    nada e nunca promove um resultado a integrado."""
    eng = Path(eng)
    cp, data = _atual(eng)
    mudou = []
    for t in data["tasks"]:
        if t["state"] != "running":
            continue
        recebidos = [r["id"] for r in data["results"]
                     if r["task_id"] == t["id"] and r["status"] == "received"]
        if recebidos:
            t["state"] = "blocked"
            t["blocker_refs"] = ["{}:por-integrar".format(recebidos[-1])]
        else:
            t["state"] = "planned"
            for ref in t["input_refs"]:
                ref.pop("sha256", None)
        mudou.append({"task": t["id"], "state": t["state"]})
    if not mudou:
        return {"operation_id": None, "receipt": None, "changed": [],
                "checkpoint": cp["data"]}
    out = _publish(eng, "task-reconcile", cp, data)
    return dict(out, changed=mudou)


def task_main(argv) -> int:
    """`workflow.py task plan|start|receive|reconcile|show …`"""
    import argparse
    ap = argparse.ArgumentParser(description="tarefas do checkpoint (publica pelo coordenador)")
    ap.add_argument("task_command", choices=["plan", "start", "receive", "reconcile", "show"])
    ap.add_argument("task_id", nargs="?", default="")
    ap.add_argument("--engagement", required=True)
    ap.add_argument("--role", default="")
    ap.add_argument("--criteria", action="append", default=[])
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--depends", action="append", default=[])
    ap.add_argument("--draft", default="")
    ap.add_argument("--start", action="store_true", help="plan: arrancar logo a seguir")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    eng = Path(a.engagement)
    if not eng.is_dir():
        eng = Path("projects") / a.engagement
    O = _op()
    try:
        if a.task_command == "plan":
            out = task_plan(eng, a.role, a.criteria, a.input, a.depends)
            if a.start:
                out = dict(task_start(eng, out["task"]), task=out["task"])
        elif a.task_command == "start":
            out = task_start(eng, a.task_id)
        elif a.task_command == "receive":
            out = task_receive(eng, a.task_id, a.draft)
        elif a.task_command == "reconcile":
            out = tasks_reconcile(eng)
        else:
            cp = read_checkpoint(eng)
            out = {"checkpoint": cp["data"], "unknown": cp["unknown"]}
    except WorkflowError as exc:
        print(json.dumps(response(False, exc.code, [_reason(str(exc))],
                                  affected_ids=[exc.detail.get("task") or ""]
                                  if exc.detail.get("task") else []),
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    except O["OperationError"] as exc:
        print(json.dumps(O["response_from_error"](exc), ensure_ascii=False, indent=2),
              file=sys.stderr)
        return 1
    out = {k: v for k, v in out.items() if k != "receipt"} if not a.json else out
    print(json.dumps(out, ensure_ascii=False, indent=2) if a.json else
          "\n".join("{:22} {}".format(k, v if not isinstance(v, (dict, list)) else
                                      json.dumps(v, ensure_ascii=False)[:160])
                    for k, v in out.items()))
    return 0


# ------------------------------------------------------------ retoma a frio (F2.4)

def _bootstrap_mod() -> dict:
    if "B" not in _CACHE:
        _CACHE["B"] = runpy.run_path(str(_HERE / "bootstrap.py"))
    return _CACHE["B"]


def _literal_request(eng: Path):
    try:
        ctx = json.loads((eng / "context.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return ctx.get("literal_request") if isinstance(ctx, dict) else None


def _decision_titles(eng: Path) -> list:
    try:
        texto = (eng / "decisions.md").read_text(encoding="utf-8")
    except OSError:
        return []
    fora = []
    for m in re.finditer(r"(?m)^#{1,4}\s*\**\s*(D-\d+)\b\s*(?:—|-)?\s*(.*)$", texto):
        fora.append({"id": m.group(1), "title": m.group(2).strip()[:120]})
    return fora


def resume(eng, budget=None) -> dict:
    """Retoma a frio (plan 04 §Retoma, T09/T16). So le; nada se escreve.

    Ordem: perfil → bootstrap (pendencia fecha tudo) → checkpoint → reconciliacao PROPOSTA
    (nao escrita) → frescura dos resultados recebidos → contexto com orcamento → proxima
    accao com a razao por que e segura. Nada depende da conversa anterior: tudo sai do
    repositorio. O que ficou fora do orcamento e dito; um bloqueio critico nunca sai calado
    — os ids de TODOS os criticos vem sempre, mesmo quando o texto nao cabe."""
    eng = Path(eng)
    B = _bootstrap_mod()
    budget = int(B["DEFAULT_BUDGET"] if budget is None else budget)
    out = {"engagement": eng.name, "ok": False, "code": None, "limitations": [],
           "objective": None, "authorizations": [], "tasks": {}, "active_task": None,
           "results_pending": [], "reconcile_proposal": [], "blockers": [],
           "context": {}, "next_action": None, "input_revision": None}

    # 1. perfil
    perfil = validate_profile(eng) if profile_of(eng)["kind"] != UNBORN else \
        response(False, INTEGRITY_FAILURE, [_reason("engagement sem `_state.json`")])
    if not perfil["ok"]:
        out.update(code=perfil["code"], limitations=perfil["reasons"],
                   next_action=(perfil["next_actions"] or [{"action": "/status",
                                                            "reason": "so leitura"}])[0])
        return out

    # 2. bootstrap, com o checkpoint no read-set: uma escrita nele a meio repete a leitura.
    # process-map M4: o mapa entra no mesmo read-set, e o resumo sai dos bytes cujo digest
    # esta revisao validou — nunca de uma segunda leitura fora da janela.
    boot = B["bootstrap"](eng, budget, inputs=(CHECKPOINT, MAP_FILE))
    out["input_revision"] = (boot.get("snapshot") or {}).get("input_revision")
    out["limitations"] = boot.get("limitations", [])
    if not boot.get("ready"):
        codigos = [l.get("code") for l in out["limitations"]]
        primeiro = next((l for l in out["limitations"] if l.get("blocking", True)), {})
        if any(c in ("PENDING_OPERATION", "PENDING_UNREADABLE") for c in codigos):
            out["code"] = RECOVERY_REQUIRED
        elif any(c in ("AUTHORITY_UNMIRRORED", "AUTHORITY_DRIFT") for c in codigos):
            out["code"] = INTEGRITY_FAILURE
        else:
            out["code"] = RECOVERY_REQUIRED
        out["next_action"] = {"action": primeiro.get("recovery") or "/status",
                              "reason": "{} — enquanto durar, retomar decide sobre estado "
                                        "misto".format(primeiro.get("detail") or
                                                       primeiro.get("code", ""))}
        return out

    # 3. checkpoint
    try:
        cp = read_checkpoint(eng)
    except WorkflowError as exc:
        out.update(code=exc.code, limitations=out["limitations"] + [
            {"code": exc.code, "blocking": True, "detail": str(exc)}],
            next_action={"action": "inspeccionar `{}` (nunca reescrever por cima)".format(
                CHECKPOINT), "reason": str(exc)})
        return out
    data = cp["data"]

    lit = _literal_request(eng)
    out["objective"] = {"ref": (data or {}).get("objective") or "context.json#literal_request",
                        "text": lit}
    if lit is None:
        out["limitations"].append({"code": "OBJECTIVE_UNDECLARED", "blocking": False,
                                   "detail": "context.json sem literal_request — o objectivo "
                                             "nao se reconstroi, nao se inventa"})
    out["authorizations"] = _decision_titles(eng)

    if data is not None:
        estados: dict = {}
        for t in data["tasks"]:
            estados.setdefault(t["state"], []).append(t["id"])
        out["tasks"] = estados
        out["active_task"] = data.get("active_task")
        # 4. reconciliacao proposta — a mesma regra de `tasks_reconcile`, sem escrever
        for t in data["tasks"]:
            if t["state"] != "running":
                continue
            recebido = [r["id"] for r in data["results"]
                        if r["task_id"] == t["id"] and r["status"] == "received"]
            out["reconcile_proposal"].append(
                {"task": t["id"], "role": t["role"],
                 "to": "blocked" if recebido else "planned",
                 "reason": ("resultado {} recebido, por integrar".format(recebido[-1])
                            if recebido else "a correr sem prova de que corre — retomavel")})
        # 5. frescura recalculada: o que o checkpoint diz pode ja nao ser verdade
        por_id = {t["id"]: t for t in data["tasks"]}
        for r in data["results"]:
            if r["status"] != "received":
                continue
            t = por_id.get(r["task_id"])
            agora, mudados = _freshness(eng, t) if t else ("unverified", [])
            out["results_pending"].append({"result": r["id"], "task": r["task_id"],
                                           "draft": r["ref"], "freshness_recorded":
                                           r["freshness"], "freshness_now": agora,
                                           "changed": mudados})

    # 6. contexto com orcamento — criticos primeiro; os ids de todos os criticos sempre
    # Do contexto do PROPRIO bootstrap (a janela validada): os criticos incluidos com o
    # texto; os que nao couberam so com o id — nomeados, nunca calados.
    ctx = boot.get("context") or {}
    out["blockers"] = ([{"id": e["id"], "text": (e.get("text") or "")[:100]}
                        for e in ctx.get("included") or []
                        if e.get("criticality") == "critical"]
                       + [{"id": i, "text": None, "note": "fora do orcamento"}
                          for i in ctx.get("omitted_critical") or []])
    out["context"] = {"complete": ctx.get("complete"), "budget": budget,
                      "included": len(ctx.get("included") or []),
                      "omitted": [o["id"] for o in ctx.get("omitted") or []],
                      "omitted_critical": ctx.get("omitted_critical") or []}
    if ctx.get("omitted_critical"):
        out["context"]["expand"] = {
            "action": "workflow.py resume --engagement {} --budget {}".format(
                eng.name, budget + len(ctx["omitted_critical"])),
            "reason": "{} bloqueio(s) critico(s) fora do contexto — estado PARCIAL; os ids "
                      "estao em `blockers`, o texto nao coube".format(
                          len(ctx["omitted_critical"]))}

    # 6b. o mapa do processo (process-map M4), no orcamento que sobrou do contexto
    out["process_map"] = _process_map_context(eng, boot, budget - out["context"]["included"])

    # 7. proxima accao, e porque e segura
    if out["reconcile_proposal"]:
        out["next_action"] = {"action": "workflow.py task reconcile --engagement {}".format(
            eng.name), "reason": "ha tarefas `running` de uma sessao anterior; reconciliar "
                                 "antes de relancar — nunca se assume que continuam"}
    elif out["results_pending"]:
        r = out["results_pending"][0]
        out["next_action"] = (
            {"action": "resolve.py publish --engagement {} --draft {}".format(
                eng.name, r["draft"].rsplit("/", 1)[-1]),
             "reason": "resultado {} recebido e actual; integra-lo nao perde nada".format(
                 r["result"])}
            if r["freshness_now"] == "current" else
            {"action": "refazer {} sobre a revisao actual".format(r["task"]),
             "reason": "o resultado {} esta stale: mudou {}".format(
                 r["result"], ", ".join(r["changed"]) or "a base")})
    elif data is not None and data["next_actions"]:
        out["next_action"] = data["next_actions"][0]
    elif (out["process_map"] or {}).get("status") == "ok" and \
            (out["process_map"].get("freshness") or {}).get("state") == "stale":
        mudou = out["process_map"]["freshness"]["changed"]
        out["next_action"] = {
            "action": "process_map.py revalidate --engagement {} {} --assessment \"<o que "
                      "mudou>\" --by \"<papel>\"{} --out <rascunho>".format(
                          eng.name, " ".join("--source " + c["source"] for c in mudou),
                          "".join(" --reviewed " + e for c in mudou for e in c["affected"])),
            "reason": "fontes do mapa mudaram desde a versão {}: {} — registar a "
                      "reavaliação antes de o usar".format(
                          out["process_map"]["version"], "; ".join(
                              "{} ({})".format(c["source"], "âncoras iguais"
                                               if c["anchors"] == "unchanged" else
                                               "afecta " + ", ".join(c["affected"]))
                              for c in mudou))}
    elif (out["process_map"] or {}).get("status") == "ok" and \
            (out["process_map"].get("validation") or {}).get("status") != "validated":
        out["next_action"] = {"action": "/capture",
                              "reason": "o mapa do processo {} está {}: rever com o dono antes "
                                        "de o usar como validado".format(
                                            out["process_map"]["version"],
                                            out["process_map"]["validation"]["status"])}
    else:
        out["next_action"] = {"action": "/status",
                              "reason": "sem trabalho em curso no checkpoint; o marco da "
                                        "fase diz o passo seguinte"}
    out["ok"] = True
    return out


MAP_FILE = "_map/map.json"


def _process_map_context(eng: Path, boot: dict, budget: int) -> dict:
    """O resumo do mapa a partir dos bytes que o snapshot validou. Sem mapa: `absent` (a
    capacidade não foi avaliada neste engagement). Bytes diferentes dos do snapshot (uma
    escrita entre a validação e esta leitura): nada se resume — `retry`, nunca estado
    misto."""
    want = ((boot.get("snapshot") or {}).get("inputs") or {}).get(MAP_FILE, "")
    p = Path(eng) / MAP_FILE
    if not want:
        return {"status": "absent", "detail": "sem mapa do processo: capacidade não avaliada"}
    try:
        raw = p.read_bytes()
    except OSError:
        return {"status": "retry", "detail": "o mapa desapareceu depois do snapshot"}
    if hashlib.sha256(raw).hexdigest() != want:
        return {"status": "retry", "detail": "o mapa mudou depois do snapshot — repetir a "
                                             "retoma"}
    if not hasattr(_process_map_context, "_pm"):
        _process_map_context._pm = runpy.run_path(str(_HERE / "process_map.py"))
    return _process_map_context._pm["summary"](eng, "resume", raw=raw, budget=max(budget, 0))

# ------------------------------------------------------------------ CLI

def utf8_console() -> None:
    _dash()["utf8_console"]()


def main(argv=None) -> int:
    utf8_console()
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "task":
        return task_main(args[1:])
    if args and args[0] == "resume":
        import argparse
        ap = argparse.ArgumentParser(description="retoma a frio (so leitura)")
        ap.add_argument("command", choices=["resume"])
        ap.add_argument("--engagement", required=True)
        ap.add_argument("--budget", type=int, default=None)
        ap.add_argument("--json", action="store_true")
        a = ap.parse_args(args)
        eng = Path(a.engagement)
        if not eng.is_dir():
            eng = Path("projects") / a.engagement
        out = resume(eng, a.budget)
        print(json.dumps(out, ensure_ascii=False, indent=2) if a.json else
              "\n".join("{:18} {}".format(k, json.dumps(v, ensure_ascii=False)[:200])
                        for k, v in out.items()))
        return 0 if out["ok"] else 1
    import argparse
    ap = argparse.ArgumentParser(description="perfil de workflow handoff-v1 (so leitura)")
    ap.add_argument("command", choices=["check"])
    ap.add_argument("--engagement")
    ap.add_argument("--pack")
    ap.add_argument("--profile")
    ap.add_argument("--route")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.engagement:
        eng = Path(a.engagement)
        if not eng.is_dir():
            eng = Path("projects") / a.engagement
        out = validate_profile(eng)
    else:
        out = validate_profile(pack=a.pack, profile=a.profile, route=a.route, birth=True)
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("ok" if out["ok"] else out["code"])
        for r in out["reasons"]:
            print("  - " + r["detail"])
        for n in out["next_actions"]:
            print("  -> {} ({})".format(n["action"], n["reason"]))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
