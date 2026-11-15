import os, pytest

SAMPLE_PDF_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "sample_contract.pdf")


def _auth_headers(t):
    return {"Authorization": f"Bearer {t}"}


def test_verification_report_created(registered_user):
    client, token, _ = registered_user
    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()
    upload = client.post(
        "/documents/upload",
        headers=_auth_headers(token),
        files={"file": ("sample_contract.pdf", pdf_bytes, "application/pdf")},
    )
    doc_id = upload.json()["id"]
    query_resp = client.post(
        "/query/",
        headers=_auth_headers(token),
        json={"document_id": doc_id, "question": "What is the payment amount?"},
    )
    query_id = query_resp.json()["id"]

    verify_resp = client.post(
        "/verify/",
        headers=_auth_headers(token),
        json={"query_record_id": query_id},
    )
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert "claims" in data
    assert isinstance(data["overall_score"], float)
    for claim in data["claims"]:
        assert "is_grounded" in claim
        assert isinstance(claim["is_grounded"], bool)
