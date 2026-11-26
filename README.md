# cv-links

Tracked links for my CV. Each application gets its own short URL
(e.g. `https://amirtqa9.github.io/k7m2p`) that records the visit in
[GoatCounter](https://www.goatcounter.com) and instantly redirects to
[github.com/amirtqa9](https://github.com/amirtqa9).

## One-time setup

1. **GoatCounter** – sign up free at goatcounter.com with the code `amirtqa9`
   (dashboard: `https://amirtqa9.goatcounter.com`). If that code is taken,
   pick another and put it in `config.json`.
2. **Repo** – create a public repo named **`amirtqa9.github.io`** and push these files.
   - Already have a site there? Use any repo name (e.g. `go`) and set
     `"base_path": "go"` in `config.json` → links become `amirtqa9.github.io/go/<code>`.
3. **Pages** – repo *Settings → Pages → Source: GitHub Actions*.
4. Push to `main`. The *Deploy tracked links* action builds and publishes.
   Its run summary lists every link.

## Adding a link for an application

From a computer:

```bash
python add_link.py "Wix - Data Analyst"          # random code, label stored
python add_link.py "Wix - Data Analyst" --private # label kept only in private_links.csv
git add links.csv && git commit -m "add link" && git push
```

From the phone: edit `links.csv` in the GitHub web editor and add a line
`code,label` (code = a-z, 0-9, `-`). Commit → it deploys in ~1 minute.

## Reading the stats

GoatCounter dashboard → each **path** (`/k7m2p`) is one application, the
**title** shows the label. Also tracked:

- `/` – someone opened the bare site URL
- `/unknown/...` – a mistyped or deleted code (still redirected to GitHub)

Counting runs in JavaScript, so most email link-scanners and bots that only
fetch the HTML are **not** counted.

## Privacy note

A free GitHub Pages site requires a public repo, so labels in `links.csv` are
public. Use `--private` (or leave the label empty) to keep company names out
of the repo; random codes can't be guessed. Alternatively, GitHub Pro (free with
the GitHub Student Developer Pack) allows Pages from a private repo.
