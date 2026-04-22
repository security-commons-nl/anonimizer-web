# anonimizer-web

> Browser-gebaseerde UI voor de anonimizer — verwijder persoonsgegevens uit documenten zonder Python-kennis.


[![Bijdragen](https://img.shields.io/badge/📝_Open_een_bericht-238636?style=for-the-badge)](../../issues/new/choose)&nbsp;&nbsp;&nbsp;&nbsp;[![Discussions](https://img.shields.io/badge/💬_Meepraten_in_discussions-0969da?style=for-the-badge)](../../discussions)

👉 **Iets delen, feedback geven of een vraag stellen?** Klik op een van de knoppen hierboven — geen Git-ervaring nodig. Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor meer opties.

Gebouwd voor CISO's en ISO's die documenten willen anonimiseren voordat ze ze delen via de [kennisbank](https://github.com/security-commons-nl/kennisbank). Zelfde interactieve flow als de [anonimizer CLI](https://github.com/security-commons-nl/anonimizer), maar in de browser.

---

## Wat het doet

1. Upload een document (PDF, Word, PowerPoint, Excel, Markdown, HTML)
2. AI detecteert namen, e-mailadressen en organisatienamen
3. Jij bevestigt of past per gevonden entiteit aan
4. Download het geanonimiseerde document als `.md` + `.html` in een zip

---

## Installatie (lokaal via Docker)

### 1. Vereisten

- Docker + Docker Compose — [docs.docker.com](https://docs.docker.com/get-docker/)
- Een Mistral API-sleutel — [console.mistral.ai](https://console.mistral.ai/)

### 2. Haal de code op

```bash
git clone https://github.com/security-commons-nl/anonimizer-web.git
cd anonimizer-web
cp .env.example .env
```

Open `.env` en vul een willekeurige sleutel in:

```bash
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### 3. Starten

```bash
docker compose up
```

De eerste keer duurt dit langer — Docker downloadt de anonimizer-core en alle dependencies.

### 4. Openen

Ga naar [http://localhost:5000](http://localhost:5000)

---

## Gebruik

1. Upload je document
2. Vul je Mistral API-sleutel in (wordt nooit opgeslagen op de server)
3. Optioneel: voeg standaard-vervangingen toe in YAML (bijv. jouw gemeentenaam)
4. Review de AI-suggesties per entiteit
5. Download de geanonimiseerde versie

---

## Privacy

- De API-sleutel staat alleen in je sessie (signed cookie), nooit op de server
- Het document wordt verwijderd na download
- Geen database, geen logging van documentinhoud
- AI-verwerking via Mistral EU-API — data blijft in Europa
- Volledig lokaal draaien via Ollama: stel `AI_API_BASE=http://host.docker.internal:11434/v1` en `AI_API_KEY=ollama` in als omgevingsvariabelen

---

## Meer documentatie

- [Gebruik](docs/gebruik.md) — stap-voor-stap voor CISO's en eindgebruikers
- [Architectuur](docs/architectuur.md) — hoe het gebouwd is en waarom
- [Configuratie](docs/configuratie.md) — omgevingsvariabelen en productie-setup
- [Roadmap](ROADMAP.md)
- [anonimizer CLI](https://github.com/security-commons-nl/anonimizer)

---

## Bijdragen

Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor hoe je iets kan delen, melden of verbeteren — met of zonder Git-ervaring.

---

## Principes

Dit project volgt de [architectuur- en communityprincipes](https://github.com/security-commons-nl/.github/blob/main/PRINCIPLES.md) van security-commons-nl: EU-soevereiniteit, AI altijd adviserend, auditbaarheid by design, least privilege en open source als standaard.
