"""Standalone lead agent: one loop, the skill library, and the workspace tools.

    python -m docloop.agent examples/events/retire-csv.json --docs examples/docs --model gpt-5
    python -m docloop.agent examples/events/retire-csv.json --docs examples/docs --demo   (no API key)

The lead agent keeps the whole context. It may hand one bounded job to a
subagent that starts with a clean context and returns a short report. Neither
can write to the docs: `approve` and `apply` are never registered as tools.
"""
from __future__ import annotations

import argparse
import inspect
import json
import os
import re
from pathlib import Path
from typing import Any, Callable, Protocol

from .workspace import Workspace

SKILLS_DIR = Path(os.environ.get("DOCLOOP_SKILLS", Path(__file__).resolve().parent.parent / "skills"))
_FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def list_skills() -> dict[str, str]:
    """Skill name -> one-line description, read from each SKILL.md front matter."""
    found = {}
    for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        match = _FRONT.match(skill_file.read_text(encoding="utf-8"))
        meta = dict(line.split(":", 1) for line in match.group(1).splitlines() if ":" in line) if match else {}
        found[meta.get("name", skill_file.parent.name).strip()] = meta.get("description", "").strip()
    return found


def load_skill(name: str) -> str:
    skill_file = SKILLS_DIR / name / "SKILL.md"
    if not skill_file.is_file():
        raise KeyError(f"No such skill: {name}. Available: {', '.join(list_skills())}")
    return _FRONT.sub("", skill_file.read_text(encoding="utf-8"), count=1)


class Model(Protocol):
    def complete(self, messages: list[dict], tools: list[dict]) -> dict:
        """Return {"content": str, "tool_calls": [{"id", "name", "arguments": dict}]}."""


class OpenAICompatibleModel:
    """Any endpoint that speaks the OpenAI chat-completions tool-calling format."""

    def __init__(self, model: str, base_url: str | None = None, api_key: str | None = None):
        from openai import OpenAI  # optional dependency
        self.client = OpenAI(base_url=base_url or os.environ.get("OPENAI_BASE_URL"),
                             api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self.model = model

    def complete(self, messages: list[dict], tools: list[dict]) -> dict:
        response = self.client.chat.completions.create(model=self.model, messages=messages, tools=tools)
        message = response.choices[0].message
        calls = [{"id": c.id, "name": c.function.name, "arguments": json.loads(c.function.arguments or "{}")}
                 for c in (message.tool_calls or [])]
        return {"content": message.content or "", "tool_calls": calls}


class ScriptedModel:
    """A stand-in model that follows a fixed script. For tests and the offline demo."""

    def __init__(self, script: list[Callable[[list[dict]], dict]]):
        self.script = list(script)

    def complete(self, messages: list[dict], tools: list[dict]) -> dict:
        if not self.script:
            return {"content": "Done.", "tool_calls": []}
        return self.script.pop(0)(messages)


def _schema(fn: Callable) -> dict:
    params = [p for p in inspect.signature(fn).parameters if p != "self"]
    return {"type": "function", "function": {
        "name": fn.__name__, "description": inspect.getdoc(fn) or "",
        "parameters": {"type": "object", "properties": {p: {"type": "string"} for p in params}, "required": params}}}


WORKER_TOOLS = ("read_page", "search_pages", "propose_edit", "propose_notice", "load_skill")


class LeadAgent:
    def __init__(self, workspace: Workspace, model: Model, max_steps: int = 30, log: Callable[[str], None] = print):
        self.ws, self.model, self.max_steps, self.log = workspace, model, max_steps, log
        self.tools: dict[str, Callable] = {name: getattr(workspace, name) for name in Workspace.AGENT_TOOLS}
        self.tools["load_skill"] = self._load_skill
        self.tools["delegate"] = self._delegate
        assert not set(Workspace.HUMAN_TOOLS) & set(self.tools), "the human gate must never be a model tool"

    def _load_skill(self, name: str) -> str:
        """Load the full instructions of one skill from the library, by name."""
        return load_skill(name)

    def _delegate(self, brief: str) -> str:
        """Hand one bounded job to a subagent with a clean context. The brief must stand alone: goal, page ids, constraints, what to report."""
        system = ("You are a subagent. You see only this brief. Do exactly what it asks with the tools you have, "
                  "then reply with a report of at most six lines: what you did, which pages, any doubt. "
                  "You cannot write to the docs; you can only propose.")
        return self._loop(system, brief, {k: self.tools[k] for k in WORKER_TOOLS}, depth=1)

    def _loop(self, system: str, task: str, tools: dict[str, Callable], depth: int = 0) -> str:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": task}]
        schemas = [_schema(fn) for fn in tools.values()]
        pad = "    " * depth
        for _ in range(self.max_steps):
            reply = self.model.complete(messages, schemas)
            calls = reply.get("tool_calls") or []
            assistant: dict[str, Any] = {"role": "assistant", "content": reply.get("content", "")}
            if calls:
                assistant["tool_calls"] = [{"id": c["id"], "type": "function", "function": {
                    "name": c["name"], "arguments": json.dumps(c["arguments"])}} for c in calls]
            messages.append(assistant)
            if not calls:
                return reply.get("content", "")
            for call in calls:
                name, args = call["name"], call["arguments"]
                if name not in tools:
                    result = f"ERROR: no such tool '{name}'. Available: {', '.join(tools)}"
                else:
                    try:
                        out = tools[name](**args)
                        result = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
                    except Exception as exc:  # the model reads the error and corrects course
                        result = f"ERROR: {exc.args[0] if exc.args else exc}"
                shown = ", ".join(f"{k}={str(v)[:40]!r}" for k, v in args.items() if k != "new_body")
                self.log(f"{pad}-> {name}({shown})" + ("  [failed]" if result.startswith("ERROR") else ""))
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
        return "Stopped: step limit reached before the task was finished."

    def run(self, event_file: str) -> str:
        catalogue = "\n".join(f"- {name}: {desc}" for name, desc in list_skills().items() if name != "docs-change-lead")
        system = (load_skill("docs-change-lead") + "\n\n## Other skills you can load with load_skill\n" + catalogue)
        return self._loop(system, f"Handle the change event in this file: {event_file}", self.tools)


def demo_script(event_file: str, ws: Workspace) -> list[Callable]:
    """A scripted run of the retire-csv example, so the loop can be shown without a model."""
    event_id = json.loads(Path(event_file).read_text(encoding="utf-8"))["id"]
    call = lambda i, name, **a: {"content": "", "tool_calls": [{"id": f"c{i}", "name": name, "arguments": a}]}

    def draft(_messages):
        body = ws.read_page("charts/exporting-data")["body"]
        new = body.replace("3. Choose **CSV (legacy)** or **CSV** from the Export menu.",
                           "3. Choose **CSV** from the Export menu.").replace(
            "The legacy CSV format keeps the column order used before version 4.",
            "The legacy CSV option was retired on 15-JAN-2027.")
        return call(6, "propose_edit", event_id=event_id, page_id="charts/exporting-data", new_body=new,
                    rationale="The legacy CSV export retires on 15-JAN-2027.")

    return [
        lambda m: call(1, "classify_event", event_file=event_file),
        lambda m: call(2, "route_event", event_file=event_file),
        lambda m: call(3, "find_affected_pages", event_file=event_file),
        lambda m: call(4, "delegate", brief=f"Event {event_id}: the legacy CSV export retires on 15-JAN-2027. "
                       "Update page charts/exporting-data so it no longer offers the legacy option and states the retirement date. "
                       "Change nothing else. Propose the edit and report."),
        lambda m: call(5, "read_page", page_id="charts/exporting-data"),   # subagent turn 1
        draft,                                                               # subagent turn 2
        lambda m: {"content": "Proposed one edit to charts/exporting-data: removed the legacy option, added the retirement date. No doubts.", "tool_calls": []},
        lambda m: call(7, "propose_notice", event_id=event_id,
                       subject="Atlas Charts: Legacy CSV export retires 15-JAN-2027",
                       body="On 15-JAN-2027 the legacy CSV export option will be removed. Use the CSV option in the Export menu instead. Contact support if you need help switching."),
        lambda m: call(8, "review_status", event_id=event_id),
        lambda m: {"content": f"Package ready for review. Run: docloop status {event_id}, then docloop approve {event_id} --reviewer <you>.", "tool_calls": []},
    ]


def _safe_console() -> None:
    """Never crash on a console that cannot show a character (older Windows code pages)."""
    import sys
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="docloop-agent", description="Run the lead agent on one change event.")
    parser.add_argument("event_file")
    parser.add_argument("--docs"); parser.add_argument("--home")
    parser.add_argument("--model", default=os.environ.get("DOCLOOP_MODEL", ""))
    parser.add_argument("--base-url", help="OpenAI-compatible endpoint. Default: $OPENAI_BASE_URL")
    parser.add_argument("--demo", action="store_true", help="scripted run of the retire-csv example, no model needed")
    args = parser.parse_args(argv)
    _safe_console()
    ws = Workspace(args.docs, args.home)
    if args.demo:
        model: Model = ScriptedModel(demo_script(args.event_file, ws))
    elif args.model:
        model = OpenAICompatibleModel(args.model, args.base_url)
    else:
        parser.error("give --model (with OPENAI_API_KEY set) or use --demo")
    print(LeadAgent(ws, model).run(args.event_file))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
