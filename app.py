"""anonimizer-web — Flask UI voor de anonimizer CLI."""
import io
import os
import pathlib
import sys
import tempfile
import uuid
import zipfile

import markdown as md
import yaml
from flask import (Flask, redirect, render_template, request,
                   send_file, session, url_for)
from flask_session import Session

# Anonimizer core: Docker mount op /anonimizer, lokaal via env var
_anonimizer_path = pathlib.Path(os.environ.get("ANONIMIZER_PATH", "/anonimizer"))
if str(_anonimizer_path) not in sys.path:
    sys.path.insert(0, str(_anonimizer_path))

from converter import to_markdown  # noqa: E402
from detector import detect        # noqa: E402
from replacer import apply         # noqa: E402

# Tijdelijke opslag voor documenttekst (te groot voor cookies)
_TMP = pathlib.Path(tempfile.gettempdir()) / "anonimizer-web"
_TMP.mkdir(exist_ok=True)
(_TMP / "sessions").mkdir(exist_ok=True)

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", os.urandom(32).hex()),
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR=str(_TMP / "sessions"),
    SESSION_PERMANENT=False,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=1800,  # 30 min
    MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50 MB
)
Session(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _opslaan_tekst(tekst: str) -> str:
    sid = str(uuid.uuid4())
    (_TMP / sid).write_text(tekst, encoding="utf-8")
    return sid


def _lees_tekst(sid: str) -> str:
    if not sid:
        return ""
    pad = _TMP / sid
    return pad.read_text(encoding="utf-8") if pad.exists() else ""


def _verwijder_tekst(sid: str) -> None:
    if sid:
        pad = _TMP / sid
        if pad.exists():
            pad.unlink()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/verwerk", methods=["POST"])
def verwerk():
    bestand = request.files.get("bestand")
    api_key = request.form.get("api_key", "").strip()
    standaard_tekst = request.form.get("standaard", "").strip()

    if not bestand or not api_key:
        return render_template("upload.html",
                               fout="Bestand en API-sleutel zijn verplicht.")

    # API key instellen voor LLM-aanroepen (single-worker deployment)
    os.environ["AI_API_KEY"] = api_key
    session["api_key"] = api_key

    # Upload tijdelijk opslaan
    suffix = pathlib.Path(bestand.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_pad = tmp.name
        bestand.save(tmp_pad)

    try:
        tekst = to_markdown(pathlib.Path(tmp_pad))
    except Exception as exc:
        return render_template("upload.html",
                               fout=f"Kon bestand niet lezen: {exc}")
    finally:
        os.unlink(tmp_pad)

    # Standaard-vervangingen uit formulier (optioneel YAML)
    standaard: dict[str, str] = {}
    if standaard_tekst:
        try:
            data = yaml.safe_load(standaard_tekst)
            if isinstance(data, dict):
                standaard = data.get("vervangingen", data)
        except Exception:
            pass

    # Detectie — 3 lagen (geen geheugen in web-modus)
    auto_mapping, new_entities = detect(tekst, [], standaard)
    tekst_verwerkt = apply(tekst, auto_mapping)

    # Sla tekst op als tijdelijk bestand (kan honderden KB zijn)
    tekst_sid = _opslaan_tekst(tekst_verwerkt)

    session["filename"] = pathlib.Path(bestand.filename).stem
    session["tekst_sid"] = tekst_sid
    session["entities"] = new_entities
    session["confirmed"] = {}
    session["auto_count"] = len(auto_mapping)
    session["totaal_entities"] = len(new_entities)

    if not new_entities:
        return redirect(url_for("download"))

    return redirect(url_for("review"))


@app.route("/review")
def review():
    entities = session.get("entities", [])
    if not entities:
        return redirect(url_for("download"))

    totaal = session.get("totaal_entities", len(entities))
    index = totaal - len(entities) + 1

    return render_template(
        "review.html",
        entiteit=entities[0],
        index=index,
        totaal=totaal,
        auto_count=session.get("auto_count", 0),
    )


@app.route("/besluit", methods=["POST"])
def besluit():
    actie = request.form.get("actie")
    entities = list(session.get("entities", []))

    if not entities:
        if request.headers.get("HX-Request"):
            return _klaar_partial()
        return redirect(url_for("download"))

    huidige = entities.pop(0)
    confirmed = dict(session.get("confirmed", {}))

    if actie == "bevestig":
        vervanging = request.form.get("suggestie", huidige.get("suggestie", ""))
        confirmed[huidige["tekst"]] = vervanging
    elif actie == "eigen":
        vervanging = request.form.get("vervanging", "").strip()
        if vervanging:
            confirmed[huidige["tekst"]] = vervanging
    elif actie == "stop":
        entities.clear()
    # actie == "overslaan": gewoon verwijderen, niet opslaan

    session["entities"] = entities
    session["confirmed"] = confirmed
    session.modified = True

    if not entities or actie == "stop":
        if request.headers.get("HX-Request"):
            return _klaar_partial()
        return redirect(url_for("download"))

    totaal = session.get("totaal_entities", len(entities))
    index = totaal - len(entities) + 1

    if request.headers.get("HX-Request"):
        return render_template(
            "_entiteit_partial.html",
            entiteit=entities[0],
            index=index,
            totaal=totaal,
        )

    return redirect(url_for("review"))


def _klaar_partial():
    return render_template(
        "_klaar_partial.html",
        confirmed_count=len(session.get("confirmed", {})),
        auto_count=session.get("auto_count", 0),
    )


@app.route("/download")
def download():
    tekst = _lees_tekst(session.get("tekst_sid", ""))
    confirmed = session.get("confirmed", {})
    filename = session.get("filename", "document")

    tekst_final = apply(tekst, confirmed) if confirmed else tekst

    # HTML genereren
    html_body = md.markdown(tekst_final, extensions=["tables"])
    html_full = (
        "<!DOCTYPE html>\n"
        '<html lang="nl">\n'
        "<head><meta charset=\"utf-8\">"
        f"<title>{filename}-anoniem</title>\n"
        "<style>"
        "body{font-family:sans-serif;max-width:800px;margin:2em auto;padding:0 1em}"
        "table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:.4em .8em}"
        "</style>\n"
        "</head>\n"
        f"<body>\n{html_body}\n</body></html>"
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{filename}-anoniem.md", tekst_final)
        zf.writestr(f"{filename}-anoniem.html", html_full)
    buf.seek(0)

    # Tijdelijke bestanden opruimen
    _verwijder_tekst(session.pop("tekst_sid", ""))
    for key in ("entities", "confirmed", "auto_count", "totaal_entities", "filename"):
        session.pop(key, None)

    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{filename}-anoniem.zip",
        mimetype="application/zip",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
