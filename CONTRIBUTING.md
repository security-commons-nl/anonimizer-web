# Bijdragen aan anonimizer-web

Bedankt voor je interesse. Deze repo volgt de organisatiebrede richtlijnen van security-commons-nl:

- [CONTRIBUTING.md (org-wide)](https://github.com/security-commons-nl/.github/blob/main/CONTRIBUTING.md)
- [DOCUMENTATION-STANDARD.md](https://github.com/security-commons-nl/.github/blob/main/DOCUMENTATION-STANDARD.md)
- [PRINCIPLES.md](https://github.com/security-commons-nl/.github/blob/main/PRINCIPLES.md)

## Project-specifieke werkwijze

### Lokaal draaien

```bash
pip install -r requirements.txt
cp .env.example .env
# vul ANONIMIZER_PATH en AI_API_KEY in
python app.py
```

### Relatie met anonimizer-CLI

Deze web-UI is een Flask-wrapper rond de [anonimizer CLI](https://github.com/security-commons-nl/anonimizer). Kern-detectielogica (regex-laag, LLM, allowlist, anafoor) leeft daar. Issues over detectiekwaliteit horen in die repo.

### PRs

- UI-wijzigingen: voeg screenshot of screencast toe aan de PR-beschrijving
- Backend-wijzigingen: update `docs/architectuur.md` als request-flow verandert
