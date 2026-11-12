---
name: untangle
description: Split the current Claude Code chat into separate chats, one per topic. Shows the proposed topics first, and opens a new session for each one only after the user approves. Use when the user types /untangle or asks to untangle, split or separate this chat by topic.
---

# Untangle this chat

Splits the chat you are in into one new session per topic. The original chat is never changed.

## 1. Read the chat

Run, with SKILL_DIR set to the base directory of this skill (shown when the skill loads; it holds this file and the `untangle/` Python folder) and a file path in your scratchpad directory (or a temp folder) for OUT:

```bash
PYTHONPATH="SKILL_DIR" python3 -m untangle dump --out "OUT"
```

It needs Python 3.9 or later and nothing else.

It reads this session (from CLAUDE_CODE_SESSION_ID) and writes a numbered transcript: `[n] USER/ASSISTANT time`, then the text, then a one-line list of tools used. If the user named another session id, pass it as the first argument after `dump`. Read OUT in full (in parts if it is long). Ignore the /untangle request itself and anything after it.

## 2. Find the topics

- A topic is one piece of work or one question thread the user would want to continue on its own. Usually 2 to 6 topics. Small one-off asks that are finished go under "Done, no new chat".
- Topics can be interleaved: group messages by topic, not by position.
- A message that serves several topics (shared background, a decision that affects both) goes into each one.
- Use only what is in the transcript. Do not add facts, and do not guess at what a cut-off message said.

## 3. Show the preview and wait

Show a short table: topic number, title (under 60 characters), message numbers, and a 3 to 5 sentence brief (where it stands, what is decided, what is still open). Then ask one question: open these as new chats? The user can rename, merge, split or drop topics. Do not start any session until the user says yes.

## 4. Open one new session per approved topic

For each topic, call `mcp__ccd_session__start_session` (load it with ToolSearch first if needed) with `initiation: "user_asked"`, `context: "fresh"`, the topic title as `title`, and a prompt that holds:
1. One line: "This chat continues a topic split out of an earlier chat."
2. The brief.
3. The key content from that topic's messages: decisions, numbers, file paths, drafts and open questions, quoted where exact wording matters. Keep it under about 1,500 words.
4. The next step, if one was open, as the request to act on. If nothing was open, ask the new session to wait for the user.

Write the bold title line and one sentence before each call, as the session rules require. After all calls, list the new sessions as links and say the original chat is unchanged.

## Rules

- Never edit, move or delete the session file or any project file.
- Never start sessions before the user approves the preview.
- Do not send the transcript anywhere outside this Claude session.
