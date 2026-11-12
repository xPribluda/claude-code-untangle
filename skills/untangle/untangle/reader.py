"""Read a Claude Code session file (.jsonl) into a simple list of messages.

Only the main conversation is kept: user and assistant text, with tool calls
shortened to one-line notes. Side work (subagents), hidden thinking and
internal records are dropped. The file is only read, never changed.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"

_REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
_COMMAND_TAGS = re.compile(r"</?(command-message|command-name|command-args)>")


@dataclass
class Message:
    index: int
    role: str  # "user" or "assistant"
    text: str
    timestamp: str = ""
    tools: list[str] = field(default_factory=list)


def project_dir_for(cwd: str) -> Path:
    """Claude Code stores a project's sessions in a folder named after its path."""
    name = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(cwd))
    return PROJECTS_DIR / name


def find_session(session: str | None = None, cwd: str | None = None) -> Path:
    """Return the session file: a path, a session id, the session Claude Code is
    running in (CLAUDE_CODE_SESSION_ID), or else the newest one for cwd."""
    if not session and not cwd:
        session = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if session:
        p = Path(session).expanduser()
        if p.is_file():
            return p
        sid = session.removeprefix("local_")
        hits = list(PROJECTS_DIR.glob(f"*/{sid}.jsonl"))
        if hits:
            return hits[0]
        raise FileNotFoundError(f"No session file found for {session!r}")
    folder = project_dir_for(cwd or os.getcwd())
    files = sorted(folder.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No session files in {folder}")
    return files[0]


def _clean(text: str) -> str:
    text = _REMINDER.sub("", text)
    text = _COMMAND_TAGS.sub("", text)
    return text.strip()


def _tool_note(block: dict) -> str:
    name = block.get("name", "tool")
    inp = block.get("input") or {}
    hint = inp.get("description") or inp.get("file_path") or inp.get("query") or inp.get("command") or ""
    hint = str(hint).splitlines()[0][:100] if hint else ""
    return f"{name}: {hint}" if hint else name


def read_session(path: Path) -> list[Message]:
    messages: list[Message] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = rec.get("type")
            if kind not in ("user", "assistant") or rec.get("isSidechain") or rec.get("isMeta"):
                continue
            msg = rec.get("message") or {}
            content = msg.get("content")
            texts: list[str] = []
            tools: list[str] = []
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    btype = block.get("type")
                    if btype == "text":
                        texts.append(block.get("text", ""))
                    elif btype == "tool_use":
                        tools.append(_tool_note(block))
                    # tool_result, thinking, images: dropped
            text = _clean("\n".join(texts))
            if kind == "user" and not text:
                continue  # tool results only
            if kind == "assistant" and messages and messages[-1].role == "assistant":
                prev = messages[-1]  # one reply is stored as several records
                prev.text = "\n".join(t for t in (prev.text, text) if t)
                prev.tools.extend(tools)
                continue
            if not text and not tools:
                continue
            messages.append(Message(len(messages) + 1, kind, text, rec.get("timestamp", ""), tools))
    return messages


def to_text(messages: list[Message], max_chars: int = 2000) -> str:
    """Numbered, compact transcript for a model (or a person) to read."""
    out = []
    for m in messages:
        body = m.text if len(m.text) <= max_chars else m.text[:max_chars] + " […cut]"
        tools = f"\n  (tools: {'; '.join(m.tools[:8])})" if m.tools else ""
        out.append(f"[{m.index}] {m.role.upper()} {m.timestamp[:16]}\n{body}{tools}")
    return "\n\n".join(out)
