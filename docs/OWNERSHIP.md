# File Tree, Ownership, Contracts

Frontend: React + Vite + TypeScript. Minimal styling.

emberground/
  app/
    config.py                    [Nikhil]  — add owner/session/JWT config, Dodo/n8n keys
    db.py                        [Nikhil]  — unchanged pattern, verify pool close-on-shutdown fix
    main.py                      [Nikhil]  — fix pool-by-value import bug, register all routers
    webhook.py                   [Nikhil]  — fix input_id scheme (see §3 fix list)
    dispatcher.py                [Nikhil]  — add supervised due-inbox worker (see §3 fix list)
    transactions.py              [Sam]     — add session/business validation in run_terminal_action
    sender.py                    [Nikhil]  — fix silent-ok-false bug, redact tokens in logs
    recovery.py                  [Nikhil]  — unchanged
    model_agent.py               [Shahana] — implement real agent loop
    holds.py                     [Sam]     — implement (reuses her transaction work)
    tools/
      find_options.py            [Sam]
      propose_order.py           [Sam]
      confirm_order.py           [Sam]
      book_slot.py               [Sam]
      answer_faq.py              [Shahana] — wires Breeth
      finish_reply.py            [Shahana]
    memory/breeth_adapter.py     [Shahana]
    auth.py                      [Nikhil]  — login/session/JWT, owner membership checks
    bot_link.py                  [Nikhil]  — token issue/consume
    n8n.py                       [Nikhil]
    billing/dodo.py              [Jagdeep] — checkout + webhook, fully isolated
    owner_page/routes.py         [Jagdeep]
    evidence_panel/routes.py     [Jagdeep]
  migrations/
    001_init.sql                 (existing, unchanged)
    002_multi_business.sql       [Nikhil — sole migration owner]
  frontend/
    src/
      api/client.ts              [Ashraf]  — shared, others consume, don't edit
      pages/Login.tsx            [Ashraf]
      pages/BusinessPicker.tsx   [Ashraf]
      pages/BotLink.tsx          [Ashraf]
      components/                [Ashraf]
      pages/Stock.tsx            [Jagdeep]
      pages/Holds.tsx            [Jagdeep]
      pages/Evidence.tsx         [Jagdeep]
      pages/Billing.tsx          [Jagdeep]
  docs/
    CONTRACTS.md                 [Nikhil, authoritative, frozen after §C.1]
    OWNERSHIP.md                 [Nikhil]
    INTEGRATION_CHECKLIST.md     [Nikhil]
    DEMO_RUNBOOK.md              [Nikhil]
  AGENTS.md                      [Nikhil]
  prompts/

No one but Nikhil edits: main.py router registration, db.py, config.py, any migration file, docs/CONTRACTS.md. Everyone else's changes to shared types/schema go through Nikhil as a small PR against those files, not direct edits.
