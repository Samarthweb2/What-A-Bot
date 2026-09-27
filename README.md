# EmberGround — WhatsApp Stationery Order Agent

Scaffold generated from `plan.md` (the locked build plan — read that file first,
it is the single source of truth). This scaffold is structure only: folders,
file names, already-fixed schema/contracts transcribed verbatim, and TODO
stubs at every point that needs real logic. Nothing here is a design
decision — all design decisions are already made in `plan.md`.

## Stack assumption (stated, not invented)
Python 3.11+, FastAPI, psycopg (Postgres/Neon), Twilio SDK, httpx (n8n call),
pydantic-settings for config, uvicorn to run. If you're using a different
stack, keep the folder/section mapping below and swap the file contents.

## Run (Windows / PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # then fill in real values
uvicorn app.main:app --reload --port 8000
```

## Where each plan section lives
| Plan section | File(s) |
|---|---|
| C — Architecture | `app/main.py`, `app/webhook.py`, `app/dispatcher.py`, `app/sender.py` |
| D — Schema | `migrations/001_init.sql` |
| E — Tool contracts | `app/tools/*.py` (signatures already filled in verbatim) |
| F — Transaction & replay rules | `app/transactions.py` |
| G — Holds / n8n notification | `app/holds.py` |
| H — Dispatcher & recovery | `app/dispatcher.py`, `app/sender.py`, `app/recovery.py` |
| I — Fixture catalog | `tests/fixtures/catalog.json` (pre-filled, it's given literally in the plan) |
| J — Verification checklist | `tests/test_verification_checklist.py` |
| Language/task cases | `tests/test_language_cases.py` |
| L — Evidence panel | `app/evidence_panel/` |
| Owner page | `app/owner_page/` |

## Status tracking
`docs/STATE_LOG.md` — append an entry after every build-schedule block, in
the format Claude gave you. `docs/handoff_template.md` — the reusable
handoff template for anything you send back to Claude mid-day.

## Before you start
This scaffold transcribes only what `plan.md` already fully specifies
(schema, tool signatures, fixture data) — it makes no new architecture or
scope decisions. Confirm this kind of setup is fine to do ahead of the
event's actual start time under EmberGround's rules; if in doubt, wait
until 10:00 AM on build day to unzip and begin.
