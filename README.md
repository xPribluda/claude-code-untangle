# claude-code-untangle

Your Claude Code chat drifted across five topics? Type `/untangle`.

Claude reads the chat and shows a table of topics: a title, which messages belong to it, and a short brief of where it stands. You can rename, merge or drop topics. After you say yes, it opens one new chat per topic, filled in with what was decided and what is still open. The original chat is not changed.

Example preview:

| # | Title | Messages | Brief |
|---|---|---|---|
| 1 | Pricing page rewrite | 4–9, 21–24 | New copy drafted; the table layout is still open. |
| 2 | Signup bug | 10–20 | Root cause found in the email check; fix not tested. |
| 3 | Q3 report numbers | 25–31 | Numbers pulled; chart for slide 4 still to make. |

Works in Claude Code. New chats open automatically in the Claude desktop app (Code tab). Needs Python 3.9 or later; nothing else to install.

## Install

### As a plugin

In a Claude Code terminal session:

```
/plugin marketplace add xPribluda/claude-code-untangle
/plugin install untangle@claude-code-untangle
```

From a shell:

```bash
claude plugin marketplace add xPribluda/claude-code-untangle
claude plugin install untangle@claude-code-untangle
```

Both install for your user by default. Add `--scope project` to the install command to install for one project only.

In the Claude desktop app: click + next to the prompt box, then Plugins, Add marketplace with `xPribluda/claude-code-untangle`, then Add plugin.

### By copying the skill

Copy the `skills/untangle` folder into `~/.claude/skills/`, so you have `~/.claude/skills/untangle/SKILL.md`. Start a new chat and type `/untangle`.

## Use the reader on its own

```bash
PYTHONPATH=skills/untangle python3 -m untangle dump <session-id or path> --out transcript.txt
```

Prints a Claude Code session (from `~/.claude/projects/`) as a numbered, readable transcript. The session file is only read, never changed.

## License

MIT
