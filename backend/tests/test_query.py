import os
import pytest

SAMPLE_PDF_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "sample_contract.pdf")


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _upload_and_query(client, token):
    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()
    upload = client.post(
        "/documents/upload",
        headers=_auth_headers(token),
        files={"file": ("sample_contract.pdf", pdf_bytes, "application/pdf")},
    )
    doc_id = upload.json()["id"]
    resp = client.post(
        "/query/",
        headers=_auth_headers(token),
        json={"document_id": doc_id, "question": "What is the monthly payment amount?"},
    )
    return resp, doc_id


def test_query_returns_answer_with_citations(registered_user):
    client, token, _ = registered_user
    resp, _ = _upload_and_query(client, token)
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert isinstance(data["citations"], list)


def test_query_on_other_user_document_forbidden(registered_user, second_user):
    client, token, _ = registered_user
    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()
    upload = client.post(
        "/documents/upload",
        headers=_auth_headers(token),
        files={"file": ("sample_contract.pdf", pdf_bytes, "application/pdf")},
    )
    doc_id = upload.json()["id"]

    _, other_token = second_user
    resp = client.post(
        "/query/",
        headers=_auth_headers(other_token),
        json={"document_id": doc_id, "question": "What is the monthly payment?"},
    )
    assert resp.status_code == 403


def test_query_history_returns_only_users_own(registered_user, second_user):
    client, token, _ = registered_user
    _upload_and_query(client, token)

    _, other_token = second_user
    resp = client.get("/query/history", headers=_auth_headers(other_token))
    assert resp.status_code == 200
    assert resp.json() == []
