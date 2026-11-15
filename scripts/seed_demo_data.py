"""
seed_demo_data.py — Create a demo user and pre-upload sample documents.
Run with: python scripts/seed_demo_data.py
The backend must be running at http://localhost:8000.
"""
import os, sys, requests

BASE_URL = "http://localhost:8000"
DEMO_EMAIL = "demo@docvera.test"
DEMO_PASS = "demo1234"
SAMPLE_PDF = os.path.join(os.path.dirname(__file__), "..", "backend", "tests", "sample_data", "sample_contract.pdf")
SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "backend", "tests", "sample_data", "financial_table.csv")


def main():
    print("Creating demo user...")
    r = requests.post(f"{BASE_URL}/auth/register", json={"email": DEMO_EMAIL, "password": DEMO_PASS})
    if r.status_code == 409:
        print("Demo user already exists.")
    elif r.status_code == 201:
        print(f"Demo user created: {DEMO_EMAIL} / {DEMO_PASS}")
    else:
        print(f"Error: {r.status_code} {r.text}"); sys.exit(1)

    r = requests.post(f"{BASE_URL}/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASS})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for filepath, mime in [(SAMPLE_PDF, "application/pdf"), (SAMPLE_CSV, "text/csv")]:
        fname = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            resp = requests.post(
                f"{BASE_URL}/documents/upload",
                headers=headers,
                files={"file": (fname, f, mime)},
            )
        if resp.status_code == 201:
            print(f"Uploaded: {fname} -> doc_id={resp.json()['id']}, status={resp.json()['status']}")
        else:
            print(f"Upload failed for {fname}: {resp.status_code} {resp.text}")

    print("\nDemo data seeded. Log in with:")
    print(f"  Email: {DEMO_EMAIL}")
    print(f"  Password: {DEMO_PASS}")


if __name__ == "__main__":
    main()
