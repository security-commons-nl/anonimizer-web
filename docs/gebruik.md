# Gebruik — anonimizer-web

> Voor CISO's, ISO's en andere professionals die documenten willen anonimiseren voor publicatie in de kennisbank.

---

## Voor wie is dit?

Professionals in de publieke sector die interne documenten willen delen (beleid, risicoanalyses, aanpakken) maar eerst persoonsgegevens en organisatiespecifieke informatie moeten verwijderen. Geen Python-kennis vereist.

---

## Eerste keer opstarten

Zie [README.md](../README.md) voor installatie via Docker. Zodra de container draait:

1. Ga naar [http://localhost:5000](http://localhost:5000)
2. Je ziet het uploadformulier

---

## De workflow stap voor stap

### Stap 1 — Document uploaden

- Kies een bestand (PDF, Word, PowerPoint, Excel, Markdown, HTML of TXT)
- Vul je Mistral API-sleutel in (gratis aan te maken via [console.mistral.ai](https://console.mistral.ai/))
- Optioneel: voeg standaard-vervangingen toe in YAML (zie hieronder)
- Klik **Verwerken**

### Stap 2 — Automatische vervangingen

De tool past direct en zonder tussenkomst toe:
- Alles wat je hebt opgegeven in het standaard-YAML-veld
- Afbeeldingen worden vervangen door `[AFBEELDING VERWIJDERD]`

Je ziet daarna hoeveel vervangingen automatisch zijn toegepast.

### Stap 3 — Interactieve review

Voor elke nieuw gedetecteerde entiteit (naam, e-mailadres, organisatie) verschijnt een kaartje:

```
Persoon: "Jan de Vries"
Suggestie van AI: "de CISO"

[Akkoord met suggestie]  [Gebruik eigen tekst]  [Overslaan]  [Stop & download]
```

- **Akkoord** — gebruik de AI-suggestie
- **Eigen tekst** — typ zelf een vervanging
- **Overslaan** — laat deze ongewijzigd staan
- **Stop & download** — sla de rest over en ga direct naar de download

### Stap 4 — Download

Na de review download je een `.zip` met:
- `<bestandsnaam>-anoniem.md` — platte tekst, klaar voor de kennisbank
- `<bestandsnaam>-anoniem.html` — opgemaakte versie voor preview

---

## Standaard-vervangingen (YAML)

Met het optionele YAML-veld kun je vaste vervangingen opgeven die altijd en stil worden toegepast — handig voor namen van je gemeente of regio:

```yaml
vervangingen:
  "Gemeente Leiden": VOORBEELDGEMEENTE
  "Leiden": VOORBEELDGEMEENTE
  "Holland Rijnland": VOORBEELDREGIO
  "j.devries@gemeentex.nl": "[e-mailadres verwijderd]"
```

Deze YAML sla je zelf op (bijv. in een tekstbestand) en plak je elke keer in het formulier. De tool bewaart dit niet tussen sessies.

---

## Bekende beperkingen

- **Geen geheugen tussen sessies** — bevestigde vervangingen worden niet onthouden. Gebruik de [CLI-versie](https://github.com/security-commons-nl/anonimizer) als je herhaaldelijk dezelfde documenten verwerkt.
- **Maximaal 50 MB** per bestand
- **Sessie verloopt na 30 minuten** — bij inactiviteit gaat de sessie verloren en moet je opnieuw beginnen
- **AI detecteert niet alles** — controleer het resultaat altijd zelf voordat je publiceert
