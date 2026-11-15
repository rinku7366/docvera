import struct, zlib, os

def create_minimal_pdf(path: str, text: str = "This agreement is effective from January 1 2024. The party agrees to pay 500 USD monthly."):
    """
    Create a minimal valid PDF file with given text, using only stdlib.
    No external libraries required — useful for test fixture generation.
    """
    # Build a simple PDF structure
    content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj

4 0 obj
<< /Length {len(text) + 50} >>
stream
BT
/F1 12 Tf
50 750 Td
({text}) Tj
ET
endstream
endobj

5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

xref
0 6
0000000000 65535 f 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
0
%%EOF
"""
    with open(path, "wb") as f:
        f.write(content.encode("latin-1"))

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
create_minimal_pdf(
    os.path.join(os.path.dirname(__file__), "sample_contract.pdf"),
    "This agreement is effective from January 1 2024. The party agrees to pay 500 USD monthly."
)
print("Sample PDF created.")
