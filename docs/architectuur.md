# Architectuur — anonimizer-web

---

## Overzicht

```
Browser
  │
  │ HTTP (htmx — gedeeltelijke page-updates)
  ▼
Flask app (app.py)
  │
  ├── converter.py + converters/   ← tekst extraheren uit document
  ├── detector.py                  ← 3-laags NER (standaard → geheugen → LLM)
  ├── replacer.py                  ← vervangingen toepassen op tekst
  └── llm_client.py                ← Mistral EU API (OpenAI-compatible)
```

De web app is een dunne laag bovenop de [anonimizer-core](https://github.com/security-commons-nl/anonimizer). Alle logica voor conversie, detectie en vervanging staat in die repo. De web app regelt alleen de HTTP-afhandeling, sessieopslag en de download.

---

## Technologieën

| Onderdeel | Keuze | Reden |
|---|---|---|
| Web framework | Flask | Lichtgewicht, Python, hergebruikt anonimizer-core direct |
| Frontend interactiviteit | htmx | Geen JavaScript-framework nodig, werkt met server-rendered HTML |
| Sessieopslag | Flask-Session (filesystem) | Documenten zijn te groot voor cookies (4 KB limiet) |
| Productieserver | Gunicorn (1 worker) | Single-worker voorkomt race conditions op os.environ voor API key |
| Container | Docker | Reproduceerbare omgeving, bundelt anonimizer-core via git clone |
| Reverse proxy | Caddy | Automatisch HTTPS, minimale configuratie |
| Frontend JS | htmx 2.0.4 (gebundeld) | Geen CDN-afhankelijkheid op runtime — EU-soevereiniteit |

---

## Codestructuur

```
anonimizer-web/
├── app.py                        ← Flask routes en sessiebeheer
├── templates/
│   ├── base.html                 ← Layout met htmx script tag
│   ├── upload.html               ← Stap 1: bestand + API key
│   ├── review.html               ← Stap 2: review-pagina (laadt partial)
│   ├── _entiteit_partial.html    ← htmx partial: één entiteit-kaartje
│   └── _klaar_partial.html       ← htmx partial: klaar-melding + download
├── static/
│   ├── style.css                 ← Vanilla CSS, geen framework
│   └── htmx.min.js               ← Gebundeld (niet via CDN)
├── docs/                         ← Documentatie (deze map)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Sessiestrategie

Flask-Session slaat sessies op als bestanden in `/tmp/anonimizer-web/sessions/`. In de sessie-cookie staat alleen een sessie-ID. De sessie bevat:

| Sleutel | Inhoud |
|---|---|
| `api_key` | Mistral API key (alleen in sessie, nooit op disk als los bestand) |
| `tekst_sid` | UUID — verwijst naar tijdelijk tekstbestand in `/tmp/anonimizer-web/` |
| `entities` | Lijst van nog te reviewen entiteiten |
| `confirmed` | Dict van bevestigde vervangingen `{origineel: vervanging}` |
| `auto_count` | Aantal automatisch toegepaste vervangingen |
| `totaal_entities` | Totaal voor de voortgangsbalk |
| `filename` | Originele bestandsnaam (zonder extensie) |

Documenten worden als losse bestanden opgeslagen (niet in de sessie zelf) omdat ze te groot zijn voor cookies én voor de sessieopslag. Na download worden ze verwijderd.

---

## htmx-flow

De review-pagina werkt zonder page-reloads via htmx:

```
GET /review
  → volledige pagina met eerste entiteit (_entiteit_partial.html geïnclude)

POST /besluit  (hx-post, hx-target="#review-area", hx-swap="innerHTML")
  → server verwerkt beslissing
  → geeft terug: volgende _entiteit_partial.html
              of _klaar_partial.html als alles gedaan is

GET /download  (link in _klaar_partial.html)
  → ZIP aanmaken en serveren, sessiedata opruimen
```

---

## Designkeuzes

**Single worker (Gunicorn `--workers 1`)**
De anonimizer-core leest de Mistral API key uit `os.environ`. Bij meerdere gelijktijdige verzoeken zou de key van gebruiker A overschreven kunnen worden door gebruiker B. Single-worker voorkomt dit. Voor schaling: gebruik een per-request context (Flask `g`) en pas `llm_client.py` aan om de key als parameter te accepteren.

**Geen database**
Privacy by design: geen persistente opslag van documentinhoud of gebruikersdata. Sessies verlopen na 30 minuten.

**htmx gebundeld in repo**
`static/htmx.min.js` staat in de repo (niet via CDN). Dit voorkomt afhankelijkheid van externe servers tijdens productiegebruik en is in lijn met het EU-soevereiniteitsbeginsel.

**`USER app` in Dockerfile**
De container draait niet als root. Least privilege principe.
