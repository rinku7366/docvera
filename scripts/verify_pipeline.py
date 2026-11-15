"""
verify_pipeline.py — End-to-end verification script for DocVera.

This script exercises the full pipeline against a running backend:
  1. Register a test user
  2. Login and get a JWT token
  3. Upload a sample PDF
  4. Query the document
  5. Verify the answer
  6. Translate text
  7. Check audit log

Run with: python scripts/verify_pipeline.py
The backend must be running at http://localhost:8000.
"""

import sys
import os
import requests

BASE_URL = "http://localhost:8000"
EMAIL = "verify_pipeline@docvera.test"
PASSWORD = "pipeline_pass_123"
SAMPLE_PDF = os.path.join(os.path.dirname(__file__), "..", "backend", "tests", "sample_data", "sample_contract.pdf")


def step(label, fn):
    print(f"\n{'='*60}")
    print(f"  STEP: {label}")
    print(f"{'='*60}")
    result = fn()
    print(f"  RESULT: OK")
    return result


def main():
    # 1. Register
    def register():
        r = requests.post(f"{BASE_URL}/auth/register", json={"email": EMAIL, "password": PASSWORD})
        if r.status_code not in (201, 409):  # 409 = already exists, ok to continue
            print(f"  ERROR: {r.status_code} {r.text}"); sys.exit(1)
        print(f"  Status: {r.status_code}")
    step("Register user", register)

    # 2. Login
    def login():
        r = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        if r.status_code != 200:
            print(f"  ERROR: {r.status_code} {r.text}"); sys.exit(1)
        token = r.json()["access_token"]
        print(f"  Token: {token[:30]}...")
        return token
    token = step("Login", login)
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Upload document
    def upload():
        with open(SAMPLE_PDF, "rb") as f:
            r = requests.post(
                f"{BASE_URL}/documents/upload",
                headers=headers,
                files={"file": ("sample_contract.pdf", f, "application/pdf")},
            )
        if r.status_code != 201:
            print(f"  ERROR: {r.status_code} {r.text}"); sys.exit(1)
        data = r.json()
        print(f"  Document ID: {data['id']}, Status: {data['status']}")
        return data["id"]
    doc_id = step("Upload document", upload)

    # 4. Query
    def query():
        r = requests.post(
            f"{BASE_URL}/query/",
            headers=headers,
            json={"document_id": doc_id, "question": "What is the monthly payment amount?"},
        )
        if r.status_code != 200:
            print(f"  ERROR: {r.status_code} {r.text}"); sys.exit(1)
        data = r.json()
        print(f"  Answer (first 200 chars): {data['answer'][:200]}")
        print(f"  Citations: {len(data['citations'])} found")
        return data["id"]
    query_id = step("Query document", query)

    # 5. Verify
    def verify():
        r = requests.post(f"{BASE_URL}/verify/", headers=headers, json={"query_record_id": query_id})
        if r.status_code != 200:
            print(f"  ERROR: {r.status_code} {r.text}"); sys.exit(1)
        data = r.json()
        print(f"  Overall grounding score: {data['overall_score']:.2f}")
        for claim in data["claims"]:
            symbol = "✓" if claim["is_grounded"] else "✗"
            print(f"  {symbol} {claim['claim'][:80]}")
        return data
    step("Verify answer", verify)

    # 6. Translate
    def translate():
        r = requests.post(
            f"{BASE_URL}/translation/text",
            headers=headers,
            json={"text": "The party agrees to pay 500 USD monthly.", "target_lang": "hi"},
        )
        if r.status_code == 200:
            print(f"  Translated: {r.json()['translated_text']}")
        elif r.status_code == 503:
            print(f"  Translation service not available (deep-translator not installed) — skipping.")
        else:
            print(f"  ERROR: {r.status_code} {r.text}"); sys.exit(1)
    step("Translate text", translate)

    # 7. Audit log
    def audit():
        r = requests.get(f"{BASE_URL}/audit/", headers=headers)
        if r.status_code != 200:
            print(f"  ERROR: {r.status_code} {r.text}"); sys.exit(1)
        actions = [log["action"] for log in r.json()]
        print(f"  Audit events: {actions}")
        assert "document.upload" in actions, "Upload not in audit log!"
        assert "query.ask" in actions, "Query not in audit log!"
    step("Check audit trail", audit)

    print(f"\n{'='*60}")
    print(f"  ALL STEPS PASSED — pipeline verified end-to-end.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
