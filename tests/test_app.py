"""Smoke-tests voor de Flask-routes.

Doel: vangen dat een dependency-bump of refactor de basis-flow breekt.
De anonimizer-core (converter/detector/replacer) wordt gemockt via conftest.
"""
import io
import zipfile


def test_index_toont_upload_form(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<form" in resp.data


def test_verwerk_zonder_bestand_toont_fout(client):
    resp = client.post("/verwerk", data={"api_key": "test-key"})
    assert resp.status_code == 200
    assert "verplicht".encode("utf-8") in resp.data


def test_verwerk_zonder_api_key_toont_fout(client):
    data = {"bestand": (io.BytesIO(b"# Test"), "test.md")}
    resp = client.post("/verwerk", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert "verplicht".encode("utf-8") in resp.data


def test_verwerk_zonder_detecties_redirect_naar_download(client):
    """Geen entiteiten gevonden = direct door naar download."""
    data = {
        "bestand": (io.BytesIO(b"# Test"), "test.md"),
        "api_key": "test-key",
    }
    resp = client.post(
        "/verwerk", data=data, content_type="multipart/form-data"
    )
    assert resp.status_code == 302
    assert "/download" in resp.location


def test_verwerk_met_detecties_redirect_naar_review(client, mock_anonimizer):
    mock_anonimizer["detect"] = lambda t, m, s: (
        {},
        [{"tekst": "Jan Jansen", "suggestie": "VOORBEELDPERSOON", "type": "persoon"}],
    )
    data = {
        "bestand": (io.BytesIO(b"# Test met Jan Jansen"), "test.md"),
        "api_key": "test-key",
    }
    resp = client.post(
        "/verwerk", data=data, content_type="multipart/form-data"
    )
    assert resp.status_code == 302
    assert "/review" in resp.location


def test_review_pagina_toont_eerste_entiteit(client, mock_anonimizer):
    mock_anonimizer["detect"] = lambda t, m, s: (
        {},
        [
            {"tekst": "Jan Jansen", "suggestie": "VOORBEELDPERSOON", "type": "persoon"},
            {"tekst": "Leiden", "suggestie": "VOORBEELDGEMEENTE", "type": "organisatie"},
        ],
    )
    data = {
        "bestand": (io.BytesIO(b"# Test"), "test.md"),
        "api_key": "test-key",
    }
    client.post("/verwerk", data=data, content_type="multipart/form-data")

    resp = client.get("/review")
    assert resp.status_code == 200
    assert b"Jan Jansen" in resp.data


def test_besluit_bevestig_gaat_naar_volgende(client, mock_anonimizer):
    mock_anonimizer["detect"] = lambda t, m, s: (
        {},
        [
            {"tekst": "Jan", "suggestie": "PERSOON_A", "type": "persoon"},
            {"tekst": "Piet", "suggestie": "PERSOON_B", "type": "persoon"},
        ],
    )
    data = {
        "bestand": (io.BytesIO(b"# Test"), "test.md"),
        "api_key": "test-key",
    }
    client.post("/verwerk", data=data, content_type="multipart/form-data")

    resp = client.post(
        "/besluit", data={"actie": "bevestig", "suggestie": "PERSOON_A"}
    )
    assert resp.status_code == 302
    assert "/review" in resp.location


def test_besluit_stop_redirect_naar_download(client, mock_anonimizer):
    mock_anonimizer["detect"] = lambda t, m, s: (
        {},
        [{"tekst": "Jan", "suggestie": "PERSOON_A", "type": "persoon"}],
    )
    data = {
        "bestand": (io.BytesIO(b"# Test"), "test.md"),
        "api_key": "test-key",
    }
    client.post("/verwerk", data=data, content_type="multipart/form-data")

    resp = client.post("/besluit", data={"actie": "stop"})
    assert resp.status_code == 302
    assert "/download" in resp.location


def test_download_levert_zip_met_md_en_html(client, mock_anonimizer):
    mock_anonimizer["apply"] = lambda t, m: "# Geanonimiseerd\n\nLorem ipsum."
    data = {
        "bestand": (io.BytesIO(b"# Origineel"), "verslag.md"),
        "api_key": "test-key",
    }
    client.post("/verwerk", data=data, content_type="multipart/form-data")

    resp = client.get("/download")
    assert resp.status_code == 200
    assert resp.mimetype == "application/zip"

    with zipfile.ZipFile(io.BytesIO(resp.data)) as zf:
        names = zf.namelist()
        assert "verslag-anoniem.md" in names
        assert "verslag-anoniem.html" in names
        md_content = zf.read("verslag-anoniem.md").decode("utf-8")
        assert "Geanonimiseerd" in md_content


def test_api_key_blijft_in_session_niet_op_disk(client, tmp_path):
    """Privacy-claim uit README: API-key alleen in session, niet op server."""
    data = {
        "bestand": (io.BytesIO(b"# Test"), "test.md"),
        "api_key": "geheime-api-sleutel-xyz",
    }
    client.post("/verwerk", data=data, content_type="multipart/form-data")

    # Doorzoek alle bestanden in tmp_path naar de raw key
    for pad in tmp_path.rglob("*"):
        if pad.is_file():
            try:
                content = pad.read_bytes()
                assert b"geheime-api-sleutel-xyz" not in content, (
                    f"API-key gevonden op disk in {pad}"
                )
            except (OSError, PermissionError):
                pass
