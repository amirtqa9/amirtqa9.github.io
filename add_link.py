#!/usr/bin/env python3
"""Add a new tracked link for one application.

    python add_link.py "Wix - Data Analyst"
    python add_link.py "Wix - Data Analyst" --code wix
    python add_link.py "Wix - Data Analyst" --private   # keep label out of the repo

Prints the URL to put on that CV. Then commit + push links.csv.
"""
import argparse
import csv
import json
import secrets
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"  # no 0/o/1/l/i look-alikes


def existing_codes() -> set[str]:
    with open(ROOT / "links.csv", newline="", encoding="utf-8") as f:
        return {(r.get("code") or "").strip().lower() for r in csv.DictReader(f)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("label", help="company / role this CV goes to")
    ap.add_argument("--code", help="custom code (default: random 5 chars)")
    ap.add_argument("--private", action="store_true",
                    help="don't store the label in links.csv (saved to private_links.csv, gitignored)")
    a = ap.parse_args()

    taken = existing_codes()
    code = (a.code or "").strip().lower()
    if code and code in taken:
        raise SystemExit(f"code {code!r} already exists")
    while not code or code in taken:
        code = "".join(secrets.choice(ALPHABET) for _ in range(5))

    with open(ROOT / "links.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([code, "" if a.private else a.label])

    if a.private:
        p = ROOT / "private_links.csv"
        new = not p.exists()
        with open(p, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["code", "label", "date"])
            w.writerow([code, a.label, date.today().isoformat()])

    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    base = cfg.get("base_path", "").strip().strip("/")
    url = f"{cfg['site_url'].rstrip('/')}{'/' + base if base else ''}/{code}"
    print(url)
    print("Now: git add links.csv && git commit -m 'add link' && git push")


if __name__ == "__main__":
    main()
