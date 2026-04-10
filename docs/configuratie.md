# Configuratie — anonimizer-web

---

## Omgevingsvariabelen

| Variabele | Verplicht | Standaard | Beschrijving |
|---|---|---|---|
| `SECRET_KEY` | Ja | — | Flask sessie-sleutel. Genereer met: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ANONIMIZER_PATH` | Nee | `/anonimizer` | Pad naar anonimizer-core. In Docker automatisch ingesteld. |
| `AI_API_BASE` | Nee | `https://api.mistral.ai/v1` | LLM API-endpoint. Overschrijf voor Ollama of andere provider. |
| `AI_MODEL_NAME` | Nee | `mistral-small-latest` | Taalmodel. |

> `AI_API_KEY` wordt **niet** als omgevingsvariabele ingesteld — die vult de gebruiker in via het uploadformulier en staat alleen in de sessie.

---

## Lokale installatie (Docker)

```bash
git clone https://github.com/security-commons-nl/anonimizer-web.git
cd anonimizer-web
cp .env.example .env
# Vul SECRET_KEY in .env
docker compose up
```

Toegankelijk op [http://localhost:5000](http://localhost:5000).

---

## Productie-installatie (VPS)

### 1. VPS vereisten

- Ubuntu 22.04 of nieuwer
- Docker + Docker Compose
- Caddy (reverse proxy + automatisch HTTPS)
- UFW (firewall)

### 2. Firewall instellen

```bash
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP (Caddy redirect)
ufw allow 443/tcp  # HTTPS
ufw enable
```

### 3. Repo clonen

```bash
mkdir -p /opt/anonimizer-web
cd /opt/anonimizer-web
git clone https://github.com/security-commons-nl/anonimizer-web.git .
cp .env.example .env
# Vul SECRET_KEY in
```

### 4. Container starten

```bash
docker compose up -d --build
```

### 5. Caddy instellen

`/etc/caddy/Caddyfile`:

```
jouw-domein.nl {
    reverse_proxy localhost:5000
}
```

```bash
systemctl reload caddy
```

Caddy regelt automatisch een Let's Encrypt certificaat.

---

## Volledig lokaal draaien (Ollama)

Geen externe API vereist. Installeer [Ollama](https://ollama.ai/) lokaal en voeg toe aan `.env`:

```bash
AI_API_BASE=http://host.docker.internal:11434/v1
```

De gebruiker vult bij de API-sleutel `ollama` in (willekeurige tekst, Ollama controleert niet).

Aanbevolen model: `mistral` of `mistral-nemo`.

---

## Anonimizer-core updaten

De Docker image kloont de anonimizer-core bij build. Om bij te werken naar de laatste versie:

```bash
docker compose up -d --build
```

Dit herhaalt de `git clone` met `--depth=1` en installeert eventuele nieuwe dependencies.
