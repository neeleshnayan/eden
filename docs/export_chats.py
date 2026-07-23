"""Export Claude Code session transcripts to readable Markdown.

The JSONL under ~/.claude/projects/<slug>/ holds every record, but most of it is
tool traffic. This keeps the conversation -- what you asked and what came back --
and drops tool calls, tool results, and the injected system-reminder blocks that
are machine plumbing rather than anything either party said.

Usage:
  python docs/export_chats.py                 # every session -> docs/chats/
  python docs/export_chats.py 67eea9eb        # one session by id prefix
"""
import glob
import json
import os
import re
import sys

PROJ = os.path.expanduser(r"~\.claude\projects\C--Users-user-Documents-eden")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chats")

# Injected plumbing that neither party actually said.
NOISE = re.compile(
    r"<system-reminder>.*?</system-reminder>"
    r"|<local-command-[a-z]+>.*?</local-command-[a-z]+>"
    r"|<command-(?:name|message|args)>.*?</command-(?:name|message|args)>"
    r"|<task-notification>.*?</task-notification>",
    re.S)


def text_of(content):
    """Flatten a message's content to plain text, dropping tool blocks."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    out = []
    for b in content:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "text":
            out.append(b.get("text", ""))
        elif b.get("type") == "thinking":
            continue          # reasoning is not conversation
        # tool_use / tool_result deliberately skipped
    return "\n".join(out)


def export(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        role = r.get("type") or r.get("role")
        if role not in ("user", "assistant"):
            continue
        # isMeta marks harness-injected text (skill bodies, hook output) that
        # arrives as a "user" turn but was never typed by anyone. isSidechain
        # marks subagent traffic, which belongs to its own conversation.
        if r.get("isMeta") or r.get("isSidechain"):
            continue
        msg = r.get("message") or {}
        body = text_of(msg.get("content", r.get("content", "")))
        body = NOISE.sub("", body).strip()
        if not body:
            continue
        # a user turn that was purely a tool result carries no prose
        rows.append((role, r.get("timestamp", "")[:19].replace("T", " "), body))

    if not rows:
        return None
    sid = os.path.basename(path).replace(".jsonl", "")
    dest = os.path.join(OUT, f"{rows[0][1][:10]}_{sid[:8]}.md")
    os.makedirs(OUT, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(f"# Session {sid[:8]}\n\n")
        f.write(f"`{rows[0][1]}` → `{rows[-1][1]}` · {len(rows)} messages\n\n---\n\n")
        for role, ts, body in rows:
            who = "🧑 **You**" if role == "user" else "🤖 **Claude**"
            f.write(f"### {who}  <sub>{ts}</sub>\n\n{body}\n\n")
    return dest, len(rows)


def main():
    want = sys.argv[1] if len(sys.argv) > 1 else None
    files = sorted(glob.glob(os.path.join(PROJ, "*.jsonl")), key=os.path.getmtime)
    total = 0
    for fn in files:
        if want and not os.path.basename(fn).startswith(want):
            continue
        res = export(fn)
        if res:
            dest, n = res
            total += n
            print(f"{n:5d} msgs -> {os.path.relpath(dest)}")
    print(f"\n{total} messages exported to {os.path.relpath(OUT)}")


if __name__ == "__main__":
    main()
