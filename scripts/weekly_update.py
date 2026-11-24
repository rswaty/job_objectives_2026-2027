#!/usr/bin/env python3
"""Draft the Tuesday team update from completed vault tasks, and email it.

Uses the checkbox date (✅ YYYY-MM-DD) only. Prefers a nested
Accomplishment line. Does not invent outcomes beyond the task text.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import smtplib
import sys
from datetime import date, timedelta
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / "Weekly"
SKIP_DIRS = {".git", ".obsidian", "Archive", "Templates", "Weekly", "scripts"}
SKIP_FILES = {"README - Start Here.md"}

TASK_RE = re.compile(r"^(\s*)-\s\[[xX]\]\s+(.*)$")
ACCOMP_RE = re.compile(r"^\s*-\s+Accomplishment:\s*(.+?)\s*$")
DONE_RE = re.compile(r"✅\s*(\d{4}-\d{2}-\d{2})")
DATE_MARK_RE = re.compile(r"[✅📅⏳]\s*\d{4}-\d{2}-\d{2}")
WIKI_LABELED_RE = re.compile(r"\[\[([^|\]]+)\|([^\]]+)\]\]")
WIKI_BARE_RE = re.compile(r"\[\[([^\]]+)\]\]")
WEEKLY_NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")

SECTION_ORDER = [
    "One Conservancy / cross-team",
    "Northwoods",
    "LANDFIRE communications",
    "LANDFIRE tools and processes",
    "LANDFIRE production support",
    "LANDFIRE analysis and publications",
    "Professional development",
]


def section_for(path: Path) -> str:
    name = path.name
    if name.startswith("01 ") or "map_rx_fires" in path.parts:
        return "One Conservancy / cross-team"
    if "Northwoods" in path.parts:
        return "Northwoods"
    if name.startswith("02 ") or "Conservation Data Lab" in path.parts:
        return "LANDFIRE communications"
    if name.startswith("03 "):
        return "LANDFIRE tools and processes"
    if name.startswith("04 "):
        return "LANDFIRE production support"
    if name.startswith("05 "):
        return "LANDFIRE analysis and publications"
    if name.startswith("06 "):
        return "Professional development"
    return path.stem


def clean_text(text: str) -> str:
    text = WIKI_LABELED_RE.sub(r"\2", text)
    text = WIKI_BARE_RE.sub(lambda m: Path(m.group(1)).name.removesuffix(".md"), text)
    text = DATE_MARK_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip(" \t-")
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text and text[-1] not in ".!?":
        text += "."
    return text


def parse_tasks(text: str) -> list[tuple[date, str]]:
    lines = text.splitlines()
    in_fence = False
    found: list[tuple[date, str]] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = TASK_RE.match(line)
        if not match:
            continue
        indent = len(match.group(1).replace("\t", "    "))
        done = DONE_RE.search(match.group(2))
        if not done:
            continue
        done_on = date.fromisoformat(done.group(1))
        accomplishments: list[str] = []
        for nxt in lines[i + 1 :]:
            if not nxt.strip():
                continue
            nxt_match = TASK_RE.match(nxt)
            nxt_indent = len(nxt[: len(nxt) - len(nxt.lstrip(" \t"))].replace("\t", "    "))
            if nxt_match and nxt_indent <= indent:
                break
            if nxt_indent <= indent and not nxt.startswith((" ", "\t")):
                break
            acc = ACCOMP_RE.match(nxt)
            if acc:
                accomplishments.append(clean_text(acc.group(1)))
            elif nxt_indent <= indent:
                break
        if accomplishments:
            found.extend((done_on, item) for item in accomplishments if item)
        else:
            bullet = clean_text(match.group(2))
            if bullet:
                found.append((done_on, bullet))
    return found


def weekly_files() -> list[tuple[date, Path]]:
    notes: list[tuple[date, Path]] = []
    if not WEEKLY.exists():
        return notes
    for path in WEEKLY.glob("*.md"):
        match = WEEKLY_NAME_RE.match(path.name)
        if match:
            notes.append((date.fromisoformat(match.group(1)), path))
    notes.sort()
    return notes


def collect(today: date) -> tuple[date, dict[str, list[str]]]:
    prior = [item for item in weekly_files() if item[0] < today]
    week_start = prior[-1][0] if prior else today - timedelta(days=7)
    prior_text = prior[-1][1].read_text(encoding="utf-8").lower() if prior else ""
    grouped: dict[str, list[str]] = {}
    for path in sorted(ROOT.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.name in SKIP_FILES:
            continue
        section = section_for(path)
        for done_on, bullet in parse_tasks(path.read_text(encoding="utf-8")):
            if done_on > today or done_on < week_start:
                continue
            if done_on == week_start and bullet.lower()[:48] in prior_text:
                continue
            if week_start < done_on <= today or done_on == week_start:
                grouped.setdefault(section, [])
                if bullet not in grouped[section]:
                    grouped[section].append(bullet)
    return week_start, grouped


def render(today: date, week_start: date, grouped: dict[str, list[str]]) -> str:
    lines = [
        f"# Weekly note — {today.isoformat()}",
        "",
        f"**To:** rswaty@tnc.org",
        f"**Subject:** Weekly update — week of {week_start.isoformat()} to {today.isoformat()}",
        "",
        "Hi team —",
        "",
        "Highlights from the past week:",
        "",
    ]
    names = [name for name in SECTION_ORDER if grouped.get(name)]
    names.extend(sorted(name for name in grouped if name not in SECTION_ORDER))
    for name in names:
        lines.append(f"## {name}")
        lines.append("")
        lines.extend(f"- {bullet}" for bullet in grouped[name])
        lines.append("")
    lines.append("—")
    lines.append("*Drafted from vault completed tasks.*")
    lines.append("")
    return "\n".join(lines)


def note_path(today: date) -> Path:
    return WEEKLY / f"{today.isoformat()}.md"


def subject_and_body(text: str) -> tuple[str, str]:
    subject = ""
    for line in text.splitlines():
        if line.startswith("**Subject:**"):
            subject = line.removeprefix("**Subject:**").strip()
            break
    body_lines = []
    started = False
    for line in text.splitlines():
        if line.startswith("Hi team"):
            started = True
        if started:
            body_lines.append(line)
    body = "\n".join(body_lines).strip() or text.strip()
    if not subject:
        subject = "Weekly update"
    return subject, body


def to_html(body: str) -> str:
    parts = ["<html><body>"]
    in_list = False
    for line in body.splitlines():
        if line.startswith("## "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.strip():
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        parts.append("</ul>")
    parts.append("</body></html>")
    return "".join(parts)


def send_email(text: str) -> None:
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    username = os.environ.get("SMTP_USERNAME", "").strip()
    if not password or not username:
        sys.exit(
            "SMTP_USERNAME and SMTP_PASSWORD are required to send. "
            "Add them as GitHub Actions secrets (Microsoft 365: smtp.office365.com, port 587)."
        )
    host = os.environ.get("SMTP_HOST", "smtp.office365.com").strip() or "smtp.office365.com"
    port = int(os.environ.get("SMTP_PORT", "587") or "587")
    mail_from = os.environ.get("MAIL_FROM", "").strip() or username
    mail_to = os.environ.get("MAIL_TO", "").strip() or "rswaty@tnc.org"
    subject, body = subject_and_body(text)
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = mail_from
    message["To"] = mail_to
    message.set_content(body)
    message.add_alternative(to_html(body), subtype="html")
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)
    print(f"Sent weekly update to {mail_to}")


def build(today: date) -> str | None:
    week_start, grouped = collect(today)
    if not grouped:
        print(f"No completed tasks for the week ending {today.isoformat()}.")
        return None
    return render(today, week_start, grouped)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Note date, YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--print", action="store_true", dest="print_note", help="Print the note and do not write or send.")
    parser.add_argument("--write", action="store_true", help="Write Weekly/YYYY-MM-DD.md if it does not already exist.")
    parser.add_argument("--send", action="store_true", help="Email the note for this date.")
    args = parser.parse_args()
    today = date.fromisoformat(args.date) if args.date else date.today()
    path = note_path(today)

    if args.print_note:
        text = path.read_text(encoding="utf-8") if path.exists() else build(today)
        if text:
            print(text)
        return

    if args.write:
        if path.exists():
            print(f"Keeping existing {path.relative_to(ROOT)}")
        else:
            text = build(today)
            if text:
                WEEKLY.mkdir(exist_ok=True)
                path.write_text(text, encoding="utf-8")
                print(f"Wrote {path.relative_to(ROOT)}")

    if args.send:
        if not path.exists():
            print(f"No note at {path.relative_to(ROOT)}; nothing to send.")
            return
        send_email(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
