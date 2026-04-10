# anonimizer-web — Roadmap

> Browser-gebaseerde UI voor de [anonimizer CLI](https://github.com/security-commons-nl/anonimizer). Zelfde flow, zonder Python-kennis.

---

## Huidige staat

Repo is aangemaakt. Basisbestanden aanwezig (`app.py`, `Dockerfile`, templates, CSS). Nog niet deployed of getest.

---

## Fase 1 — Werkende MVP

Een CISO zonder technische achtergrond kan een document uploaden, AI-suggesties per entiteit reviewen, en het resultaat downloaden.

### Stack

- **Flask** — Python, hergebruikt anonimizer-core direct
- **htmx** — interactieve review zonder JavaScript-framework
- **Flask-Session** — server-side sessies (document te groot voor cookie)
- **Gunicorn** — single-worker productieserver
- **Docker** — anonimizer-core via `git clone` tijdens image build

### Gebruikersflow

```
/ (upload)
  → bestand + Mistral API key + optioneel standaard-YAML

/verwerk (POST)
  → tekst extraheren (converters/)
  → Laag 1+2: auto-mapping toepassen (standaard + session memory)
  → Laag 3: LLM NER → nieuwe entiteiten opslaan in sessie
  → redirect naar /review

/review (htmx)
  → één entiteit per keer tonen
  → POST /besluit: bevestig / eigen tekst / overslaan / stop
  → htmx swap: volgende entiteit of klaar-kaart

/download
  → alle vervangingen toepassen
  → .md + .html genereren
  → als .zip serveren
  → tijdelijke bestanden verwijderen
```

### Privacy

- Geüpload bestand opgeslagen in `/tmp`, verwijderd na download
- API key alleen in Flask session (signed cookie), nooit server-side bewaard
- Geen database, geen logging van documentinhoud
- Sessies verlopen na 30 minuten

### Implementatiestappen

- [x] `app.py` — Flask routes (/, /verwerk, /review, /besluit, /download)
- [x] `templates/` — base, upload, review, partials (_entiteit, _klaar)
- [x] `static/style.css` — minimale vanilla CSS, geen CDN-afhankelijkheden
- [x] `Dockerfile` — Python 3.12, clont anonimizer-core, downloadt htmx.min.js
- [x] `docker-compose.yml` — zie spec hieronder
- [ ] `.env.example` — zie spec hieronder
- [ ] `.gitignore` — zie spec hieronder
- [ ] `README.md` — zie spec hieronder
- [ ] Lokale testrun: `docker compose up`, document uploaden, volledige flow doorlopen
- [ ] Fix eventuele bugs na eerste test

---

### Spec: `docker-compose.yml`

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - ANONIMIZER_PATH=/anonimizer
    volumes:
      - /tmp/anonimizer-web:/tmp/anonimizer-web
    restart: unless-stopped
```

**Toelichting:**
- `SECRET_KEY` via `.env` (niet hardcoded) — Flask gebruikt dit voor sessie-signing
- Volume `/tmp/anonimizer-web` — gedeeld tussen container en host zodat sessiebestanden en documenttekst persistent zijn over container-restarts
- `ANONIMIZER_PATH=/anonimizer` — wijst naar de geclonde anonimizer-core in de container
- Geen database-service nodig — sessies op filesystem, geen persistente data

---

### Spec: `.env.example`

```bash
# Flask sessie-sleutel — genereer met: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=vervang-dit-met-een-willekeurige-sleutel

# Pad naar anonimizer-core (automatisch ingesteld in Docker)
# ANONIMIZER_PATH=/anonimizer
```

**Toelichting:**
- `.env` zelf wordt gitignored, `.env.example` staat in de repo als startpunt
- Mistral API key staat NIET in `.env` — die vult de gebruiker per sessie in via het uploadformulier
- `ANONIMIZER_PATH` is optioneel voor lokale ontwikkeling buiten Docker

---

### Spec: `.gitignore`

```
.env
__pycache__/
*.pyc
*.pyo
.pytest_cache/
static/htmx.min.js
```

**Toelichting:**
- `htmx.min.js` wordt gedownload tijdens `docker build` (zie Dockerfile), niet in de repo opgeslagen
- `.env` bevat de SECRET_KEY, nooit committen

---

### Spec: `README.md`

Structuur (volgt patroon van `anonimizer/README.md`):

```
# anonimizer-web

> [één-zin beschrijving]

## Wat het doet
  - Uploadformulier, interactieve review, download als .zip

## Installatie (lokaal via Docker)

### 1. Vereisten
  - Docker + Docker Compose

### 2. Haal de code op
  git clone ...
  cd anonimizer-web
  cp .env.example .env
  # Vul SECRET_KEY in in .env

### 3. Starten
  docker compose up

### 4. Openen
  http://localhost:5000

## Deploy (productie)
  - Zie Fase 2 in ROADMAP.md voor VPS-setup en Caddy-configuratie

## Principes
  - Verwijzing naar security-commons-nl PRINCIPLES.md
```

---

## Fase 2 — Deploy op AUTOMATIQ VPS

**Target:** `65.21.252.13` (Hetzner, Ubuntu 24.04, 2vCPU 4GB, SSH alias `automatiq`)

### Eenmalige VPS-setup

```bash
# Via: ssh automatiq
# 1. Docker installeren (apt)
# 2. Caddy installeren (reverse proxy + automatisch HTTPS)
# 3. UFW instellen: alleen 22, 80, 443
# 4. /opt/anonimizer-web aanmaken, repo clonen
```

### Caddy-configuratie

```
anonimizer.security-commons.nl {
    reverse_proxy localhost:5000
}
```

**Domein:** nog te bepalen — `anonimizer.security-commons.nl` of subdomein van een bestaand domein.

### GitHub Actions auto-deploy

```yaml
# .github/workflows/deploy.yml
# Trigger: push naar main
# Stappen: SSH → git pull → docker compose up --build -d
```

### Implementatiestappen

- [ ] Domein bepalen en DNS instellen
- [ ] VPS opzetten (Docker, Caddy, UFW)
- [ ] Eerste handmatige deploy testen
- [ ] GitHub Actions deploy workflow schrijven
- [ ] SSH deploy key instellen als GitHub Secret
- [ ] End-to-end testen op productie-URL

---

## Fase 3 — Usability & hardening

Na eerste succesvolle deploys en feedback van gebruikers.

- [ ] Session memory — door gebruiker bevestigde vervangingen bewaren over sessies (browser localStorage)
- [ ] Standaard-YAML presets — gemeentenamen vooringevuld op uploadpagina
- [ ] Foutafhandeling verbeteren — betere feedback bij verkeerde API key, onleesbaar bestand
- [ ] Rate limiting — bescherming tegen abuse
- [ ] Monitoring — Uptime-check instellen

---

## Bijdragen

Heb je ideeën of wil je bijdragen? Open een [issue](https://github.com/security-commons-nl/anonimizer-web/issues) of zie [CONTRIBUTING.md](https://github.com/security-commons-nl/.github/blob/main/CONTRIBUTING.md).
