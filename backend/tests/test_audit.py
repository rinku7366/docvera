import os, pytest

SAMPLE_PDF_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "sample_contract.pdf")


def test_audit_log_created_after_upload(registered_user):
    client, token, _ = registered_user
    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()
    client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("sample_contract.pdf", pdf_bytes, "application/pdf")},
    )
    resp = client.get("/audit/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    actions = [log["action"] for log in resp.json()]
    assert "document.upload" in actions


def test_audit_log_only_returns_own_logs(registered_user, second_user):
    client, token, _ = registered_user
    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()
    client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("sample_contract.pdf", pdf_bytes, "application/pdf")},
    )
    _, other_token = second_user
    resp = client.get("/audit/", headers={"Authorization": f"Bearer {other_token}"})
    assert resp.status_code == 200
    assert resp.json() == []
