#!/usr/bin/env python3
"""Build tracked redirect pages from links.csv into _site/.

Each row in links.csv becomes  <site_url><base_path>/<code>/  which records a
visit in GoatCounter (path = /<code>, title = label) and then redirects to the
target (your GitHub profile). Standard library only.
"""
import csv
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
CODE_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
RESERVED = {"404", "index"}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Redirecting…</title>
<link rel="canonical" href="{target_attr}">
<noscript><meta http-equiv="refresh" content="1;url={target_attr}"></noscript>
<script>
(function () {{
  var target = {target_js};
  var path = {path_js};
  var title = {title_js};
  var endpoint = {endpoint_js};
  var done = false;
  function go() {{ if (done) return; done = true; location.replace(target); }}
  try {{
    var q = "p=" + encodeURIComponent(path) +
            "&t=" + encodeURIComponent(title) +
            "&r=" + encodeURIComponent(document.referrer || "") +
            "&rnd=" + Math.random().toString(36).slice(2);
    var url = endpoint + "?" + q;
    if (window.fetch) {{
      fetch(url, {{ mode: "no-cors", keepalive: true, credentials: "omit" }}).then(go, go);
    }} else {{
      var img = new Image();
      img.onload = img.onerror = go;
      img.src = url;
    }}
  }} catch (e) {{ /* never block the redirect */ }}
  setTimeout(go, 800);
}})();
</script>
<style>body{{font:16px system-ui,sans-serif;margin:3rem;color:#444}}</style>
</head>
<body>
<p>Redirecting to <a href="{target_attr}">{target_text}</a>…</p>
</body>
</html>
"""


def js(value: str) -> str:
    # JSON is valid JS; escape "</" so a label can never close the script tag.
    return json.dumps(value).replace("</", "<\\/")


def render(cfg: dict, path_js: str, title: str) -> str:
    target = cfg["target"]
    endpoint = f"https://{cfg['goatcounter_code']}.goatcounter.com/count"
    return PAGE.format(
        target_attr=html.escape(target, quote=True),
        target_text=html.escape(target),
        target_js=js(target),
        path_js=path_js,
        title_js=js(title),
        endpoint_js=js(endpoint),
    )


def load_config() -> dict:
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    for key in ("goatcounter_code", "target", "site_url"):
        if not cfg.get(key):
            sys.exit(f"config.json: '{key}' is required")
    base = cfg.get("base_path", "").strip().strip("/")
    cfg["base_path"] = f"/{base}" if base else ""
    cfg["site_url"] = cfg["site_url"].rstrip("/")
    return cfg


def load_links() -> list[tuple[str, str]]:
    rows, seen = [], set()
    with open(ROOT / "links.csv", newline="", encoding="utf-8") as f:
        for n, row in enumerate(csv.DictReader(f), start=2):
            code = (row.get("code") or "").strip().lower()
            label = (row.get("label") or "").strip()
            if not code and not label:
                continue
            if not CODE_RE.match(code) or code in RESERVED:
                sys.exit(f"links.csv line {n}: invalid code {code!r} "
                         "(use a-z, 0-9, '-', max 40 chars)")
            if code in seen:
                sys.exit(f"links.csv line {n}: duplicate code {code!r}")
            seen.add(code)
            rows.append((code, label or code))
    return rows


def main() -> None:
    cfg = load_config()
    links = load_links()

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / ".nojekyll").write_text("")

    # Bare site URL -> counted as "/" and redirected too.
    (OUT / "index.html").write_text(render(cfg, js("/"), "Direct (no code)"), encoding="utf-8")
    # Mistyped/unknown codes still land on GitHub; counted under /unknown/<path>.
    (OUT / "404.html").write_text(
        render(cfg, '"/unknown" + location.pathname', "Unknown link"), encoding="utf-8")

    lines = ["| Label | Link |", "|---|---|"]
    for code, label in links:
        d = OUT / code
        d.mkdir()
        (d / "index.html").write_text(render(cfg, js(f"/{code}"), label), encoding="utf-8")
        url = f"{cfg['site_url']}{cfg['base_path']}/{code}"
        print(f"{url}  ->  {label}")
        lines.append(f"| {label.replace('|', '/')} | {url} |")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Tracked CV links\n\n" + "\n".join(lines) + "\n")
    print(f"Built {len(links)} link(s) into {OUT}")


if __name__ == "__main__":
    main()
