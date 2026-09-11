#!/usr/bin/env python3
"""
Fetches the Freshbox weekly menu page server-side and writes menu.json.

This runs inside GitHub Actions (a real server), not a browser, so there is
no CORS restriction at all -- this is the reliable half of the pipeline.
The static app then just reads menu.json from its own origin.
"""
import json
import re
import sys
from datetime import datetime, timezone

import html2text
import requests

URL = "https://www.freshbox.cz/tydenni-menu/"

DAY_LABELS = {
    "PONDĚLÍ": "Pondělí",
    "ÚTERÝ": "Úterý",
    "STŘEDA": "Středa",
    "ČTVRTEK": "Čtvrtek",
    "PÁTEK": "Pátek",
}

DAY_RE = re.compile(
    r"^(PONDĚLÍ|ÚTERÝ|STŘEDA|ČTVRTEK|PÁTEK)\s+(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})",
    re.IGNORECASE,
)
SOUP_RE = re.compile(r"^Pol[eé]vka\b\s*(.*)$", re.IGNORECASE)
LUNCH_RE = re.compile(r"^Ob[eě]d\s*([1-4])\b\s*(.*)$", re.IGNORECASE)
DESSERT_RE = re.compile(r"^Dezert\b\s*(.*)$", re.IGNORECASE)
SALAD_RE = re.compile(r"^Fresh sal[aá]t\b\s*(.*)$", re.IGNORECASE)


def fetch_text() -> str:
    resp = requests.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0 (compatible; freshbox-planner-bot/1.0)"})
    resp.raise_for_status()
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    converter.body_width = 0
    return converter.handle(resp.text)


def clean_item(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\*\*", "", s)
    s = re.sub(r"\|\s*[\d,]+\s*$", "", s)
    return s.strip()


def parse_weeks(text: str):
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    weeks = []
    cur_week = None
    cur_day = None

    def push_day():
        nonlocal cur_day
        if cur_day and cur_week is not None:
            cur_week["days"].append(cur_day)
        cur_day = None

    def push_week():
        nonlocal cur_week
        push_day()
        if cur_week and cur_week["days"]:
            weeks.append(cur_week)
        cur_week = None

    for raw in lines:
        line = re.sub(r"\*\*", "", raw).strip()
        dm = DAY_RE.match(line)
        if dm:
            key = dm.group(1).upper()
            if key == "PONDĚLÍ":
                push_week()
                cur_week = {"days": []}
            if cur_week is None:
                cur_week = {"days": []}
            push_day()
            d, m, y = int(dm.group(2)), int(dm.group(3)), int(dm.group(4))
            iso = f"{y:04d}-{m:02d}-{d:02d}"
            cur_day = {
                "date": iso,
                "dayName": DAY_LABELS.get(key, key),
                "soup": None,
                "lunches": [],
                "dessert": None,
                "freshSalad": None,
            }
            continue
        if cur_day is None:
            continue
        m = SOUP_RE.match(line)
        if m:
            val = clean_item(m.group(1))
            if val:
                cur_day["soup"] = val
            continue
        m = LUNCH_RE.match(line)
        if m:
            cur_day["lunches"].append({"id": f"obed{m.group(1)}", "name": clean_item(m.group(2))})
            continue
        m = DESSERT_RE.match(line)
        if m:
            val = clean_item(m.group(1))
            if val:
                cur_day["dessert"] = val
            continue
        m = SALAD_RE.match(line)
        if m:
            val = clean_item(m.group(1))
            cur_day["freshSalad"] = val or "Fresh salát"
            continue

    push_week()
    return [w for w in weeks if len(w["days"]) >= 3]


def main():
    text = fetch_text()
    weeks = parse_weeks(text)
    if not weeks:
        print("ERROR: no weeks parsed from freshbox.cz", file=sys.stderr)
        sys.exit(1)

    data = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "weeks": weeks,
    }
    with open("menu.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"OK: wrote {len(weeks)} week(s) to menu.json")


if __name__ == "__main__":
    main()
