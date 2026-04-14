# anonimizer-web — Overview

> **Navigation aid.** This article shows WHERE things live (routes, models, files). Read actual source files before implementing new features or making changes.

**anonimizer-web** is a python project built with flask.

## Scale

5 API routes · 1 library files · 3 environment variables

## Subsystems

- **[Besluit](./besluit.md)** — 1 routes — touches: auth, db, upload
- **[Download](./download.md)** — 1 routes — touches: auth, db, upload
- **[Review](./review.md)** — 1 routes — touches: auth, db, upload
- **[Verwerk](./verwerk.md)** — 1 routes — touches: auth, db, upload
- **[Infra](./infra.md)** — 1 routes — touches: auth, db, upload

## Required Environment Variables

- `AI_API_KEY` — `app.py`
- `ANONIMIZER_PATH` — `app.py`

---
_Back to [index.md](./index.md) · Generated 2026-04-14_