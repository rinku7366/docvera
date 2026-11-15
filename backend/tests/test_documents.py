import io
import os
import pytest


SAMPLE_PDF_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "sample_contract.pdf")
SAMPLE_CSV_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "financial_table.csv")


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _upload_pdf(client, token):
    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()
    resp = client.post(
        "/documents/upload",
        headers=_auth_headers(token),
        files={"file": ("sample_contract.pdf", pdf_bytes, "application/pdf")},
    )
    return resp


def test_upload_valid_pdf(registered_user):
    client, token, _ = registered_user
    resp = _upload_pdf(client, token)
    assert resp.status_code == 201
    data = resp.json()
    assert data["original_filename"] == "sample_contract.pdf"
    assert data["status"] in ("READY", "FAILED")  # processing runs synchronously


def test_upload_invalid_mime_rejected(registered_user):
    client, token, _ = registered_user
    resp = client.post(
        "/documents/upload",
        headers=_auth_headers(token),
        files={"file": ("test.exe", b"MZ\x90\x00", "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert "not supported" in resp.json()["detail"].lower()


def test_list_documents_returns_only_users_own(registered_user, second_user):
    client, token, _ = registered_user
    _upload_pdf(client, token)

    _, other_token = second_user
    resp = client.get("/documents/", headers=_auth_headers(other_token))
    assert resp.status_code == 200
    assert resp.json() == []  # second user sees no documents


def test_cross_user_document_access_forbidden(registered_user, second_user):
    client, token, _ = registered_user
    upload_resp = _upload_pdf(client, token)
    doc_id = upload_resp.json()["id"]

    _, other_token = second_user
    resp = client.get(f"/documents/{doc_id}", headers=_auth_headers(other_token))
    assert resp.status_code == 403


def test_upload_csv(registered_user):
    client, token, _ = registered_user
    with open(SAMPLE_CSV_PATH, "rb") as f:
        csv_bytes = f.read()
    resp = client.post(
        "/documents/upload",
        headers=_auth_headers(token),
        files={"file": ("financial_table.csv", csv_bytes, "text/csv")},
    )
    assert resp.status_code == 201
