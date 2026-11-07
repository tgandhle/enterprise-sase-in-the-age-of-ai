# Enterprise SASE in the Age of AI

A learning course on the controls between an organization's people, agents and the internet: web gateways, data loss prevention, zero trust network access and the logs behind them, with AI traffic as the running case. SASE products deliver these as one vendor service. This course takes them apart so you can see what each one decides.

It is the companion to [API Security in the Age of AI](https://github.com/tgandhle/api-security-in-the-age-of-ai), which looks at the same systems from the API side, and it uses the same page template, lab rules and checks.

**Reading the lessons:** Open the [hosted learning site](https://tgandhle.github.io/enterprise-sase-in-the-age-of-ai/) in a browser. You can also choose **Code > Download ZIP**, extract the archive, and open `index.html` locally. Reading the pages needs no installation or build.

## Status

One module is published. The rest are planned: see the [roadmap](https://tgandhle.github.io/enterprise-sase-in-the-age-of-ai/roadmap/).

| Module | Lesson | Python lab | Real-stack lab |
|---|---|---|---|
| 2 | [Prompt DLP under TLS inspection](https://tgandhle.github.io/enterprise-sase-in-the-age-of-ai/topics/prompt-dlp/) | [`prompt_dlp_lab.py`](labs/prompt_dlp_lab.py) | [`stack/prompt-dlp/`](stack/prompt-dlp/README.md) |

## Two kinds of lab

**Python labs** (`labs/`) are the core of every module. Python 3 standard library only, no network, deterministic output. Each lesson page publishes the real output of its lab, and `tools/check_transcripts.py` runs the lab and compares it byte for byte.

**Real-stack labs** (`stack/<slug>/`) are optional. They send the same requests through real tools, such as a TLS-inspecting proxy, and need packages the Python labs do not. No site tool or CI job runs them. Each README records the versions and the date of the run its output comes from.

```
python3 labs/prompt_dlp_lab.py
```

On Windows, use `py -3` in place of `python3`. The real-stack scripts are bash: on Windows, run them in WSL.

## Working on the site

Plain HTML, the same model as the companion course: the pages in `topics/`, `index.html`, `glossary/` and `roadmap/` are the source of truth, and `content/` is extracted from them. Read `AGENTS.md` and `CONVENTIONS.md` before changing anything.

Before committing:

```
python3 tools/check_site.py                    # links, anchors, dashes, secrets, checklist freshness
python3 tools/extract_lessons.py --check       # pages rebuild from content/
python3 tools/render_site.py                   # the shared template still reproduces every page
python3 tools/build_lab_bundles.py --check     # the .lab.js copies still match the .py files
python3 tools/extract_pages.py --check         # content/pages.json matches the home, glossary and roadmap
python3 tools/build_search_index.py --check    # assets/search-index.js matches content/
python3 tools/build_checklist.py --check       # checklist is current
python3 tools/check_applicability.py           # every checklist item has a valid applicability condition
python3 tools/check_review_dates.py --strict   # no lesson is past its review date
python3 tools/check_transcripts.py --no-skips  # runs every lab and compares it to the page
```

All ten exit 0 when the site is clean.

## Licence

Copyright (c) 2026 tgandhle. The code (`labs/`, `tools/`, `stack/`, and the site's script and stylesheet) is licensed MIT: see [LICENSE](LICENSE). Everything else, including the lessons, glossary and checklist, is licensed CC BY 4.0: see [LICENSE-CONTENT.md](LICENSE-CONTENT.md) for the exact split and the attribution to use, and [CHECKLIST-LICENSE.md](CHECKLIST-LICENSE.md) for the checklist data's own attribution line. Quoted specifications remain the property of their publishers.
