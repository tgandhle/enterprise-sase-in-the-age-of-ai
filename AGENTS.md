# AGENTS.md

Instructions for coding agents working in this repository. Read this file, `CONVENTIONS.md`, and `topics/prompt-dlp/index.html` before starting any task. The prompt DLP page is the reference implementation of the page template here: match its structure, tone and markup.

## What this project is

A static learning site that teaches the controls between an organization's people, agents and the internet, with AI traffic as the running case. It is the companion to API Security in the Age of AI (`tgandhle/api-security-in-the-age-of-ai`) and was forked from that repository's tooling on 2026-11-05. When this file is silent, that repository's `AGENTS.md` is the precedent, but never copy lesson content from it: link to it.

- Format: hand-written HTML and one shared stylesheet, `assets/site.css`. No site generator, no framework, no JavaScript build. The pages must open from a downloaded folder (`file://`). Use relative links inside this site.
- Python labs: `labs/<topic>_lab.py`. Python 3, standard library only, no network, deterministic output. They are the core of each module and are checked by `tools/check_transcripts.py`.
- Real-stack labs: `stack/<slug>/`. Optional, may use packages, never checked by CI. See the rule in `CONVENTIONS.md`.
- Links to the companion course are absolute `https://tgandhle.github.io/api-security-in-the-age-of-ai/...` links to a specific module.

## Not yet ported from the companion course

These exist there and are not here yet. Each is a decision, not a copy:

| Item | Why it is not here |
|---|---|
| `app/` (React build, analytics) | The analytics property belongs to the other course. A new one is the owner's decision. |
| `.github/workflows/` | CI configuration. Stop and ask. |
| `tools/build_coverage.py` | It pins three OWASP lists that fit API security. This course needs its own choice of lists. |
| `tools/build_review_packets.py`, `review/` | Packets are split by area of expertise; there is one lesson. |
| `QUALITY.md`, `accessibility/`, `tools/check_a11y.py`, `tools/check_labs_browser.py`, `tools/release_evidence.py` | Port when the course has enough lessons to release. |

## Stop and ask before

- Adding any dependency to a Python lab.
- Changing the severity rubric's reference model, or declaring applicability facts. Both are open owner decisions recorded in `CONVENTIONS.md`.
- Choosing or changing the licence.
- Deleting or renaming any file.
- Changing the page template structure or the claim-label scheme.
- Any git history rewrite or force push.
- Adding CI configuration.
- Publishing claims about a spec you could not open and read.

## Decisions

- **2026-11-05: Python labs are the core, real-stack labs are optional (option C).** Owner decision. A stdlib lab keeps browser runs, deterministic transcripts and every check. A real-stack lab shows what a simulation cannot, such as a pinned app failing under inspection, at the cost of being unchecked.
- **2026-11-05: Separate repository, linked to the companion course.** Owner decision. The two courses have different lab infrastructure and partly different audiences, and one course's checks should not gate the other's releases.
