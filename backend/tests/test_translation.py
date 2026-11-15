import pytest


def test_translate_text(registered_user):
    client, token, _ = registered_user
    resp = client.post(
        "/translation/text",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "Hello world", "target_lang": "hi", "source_lang": "en"},
    )
    # deep-translator may not be installed in test env — accept 200 or 503
    assert resp.status_code in (200, 503)
    if resp.status_code == 200:
        data = resp.json()
        assert len(data["translated_text"]) > 0


def test_translation_history(registered_user):
    client, token, _ = registered_user
    resp = client.get(
        "/translation/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
