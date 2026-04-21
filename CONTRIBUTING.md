# Bijdragen aan anonimizer-web

Iets delen of verbeteren? Drie manieren, van makkelijk naar technisch.

## 1. Iets aanbieden of melden — geen Git-ervaring nodig

→ [**Bijdrage aanbieden**](https://github.com/security-commons-nl/anonimizer-web/issues/new?template=bijdrage-aanbieden.md)
  Een idee of feedback over de web-UI.

→ [**Fout of verbetering**](https://github.com/security-commons-nl/anonimizer-web/issues/new?template=fout-of-verbetering.md)
  Iets klopt niet, kan beter, of mist.

Vul alleen de vragen in die voor jou relevant zijn — we helpen je met de rest.

**Geen GitHub-account?** [Maak er gratis een](https://github.com/signup) (2 minuten), of vraag iemand in je netwerk om namens jou te posten.

## 2. Meediscussiëren

→ [**Discussions**](https://github.com/orgs/security-commons-nl/discussions)

Voor vragen, ervaringen en ideeën zonder directe actie.

## 3. Voor ontwikkelaars — code aanleveren

### Relatie met anonimizer-CLI

Deze web-UI is een Flask-wrapper rond de [anonimizer CLI](https://github.com/security-commons-nl/anonimizer). Kern-detectielogica (regex, LLM, allowlist, anafoor) leeft daar. **Issues over detectiekwaliteit horen in die repo.**

### Lokale setup

```bash
pip install -r requirements.txt
cp .env.example .env
# vul ANONIMIZER_PATH en AI_API_KEY in
python app.py
```

### PRs

- UI-wijzigingen: voeg screenshot of screencast toe aan de PR-beschrijving
- Backend-wijzigingen: update `docs/architectuur.md` als de request-flow verandert

---

**Organisatiebrede richtlijnen**: [security-commons-nl/.github](https://github.com/security-commons-nl/.github/blob/main/CONTRIBUTING.md)
