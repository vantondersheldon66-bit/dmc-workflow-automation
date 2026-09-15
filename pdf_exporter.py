"""
DMC Native PDF Exporter
Uses the built-in Microsoft Edge or Google Chrome headless engine on Windows.
Zero external npm or python PDF dependencies required.
"""

import os
import subprocess
import sys

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def export_html_to_pdf(input_html_path: str, output_pdf_path: str) -> dict:
    """Exports any HTML file to high-resolution vector PDF using headless Edge."""
    if not os.path.isabs(input_html_path):
        input_html_path = os.path.join(DIRECTORY, input_html_path)
    if not os.path.isabs(output_pdf_path):
        output_pdf_path = os.path.join(DIRECTORY, output_pdf_path)

    file_uri = f"file:///{input_html_path.replace(os.sep, '/')}"

    if not os.path.exists(EDGE_PATH):
        return {"success": False, "error": "Microsoft Edge executable not found"}

    args = [
        EDGE_PATH,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        f"--print-to-pdf={output_pdf_path}",
        file_uri
    ]

    try:
        res = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
            return {
                "success": True,
                "pdf_file": os.path.basename(output_pdf_path),
                "pdf_path": output_pdf_path,
                "size_bytes": os.path.getsize(output_pdf_path)
            }
        else:
            return {"success": False, "error": res.stderr or "PDF file was not created"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    test_in = os.path.join(DIRECTORY, "output_sample_proposal.html")
    test_out = os.path.join(DIRECTORY, "output_sample_proposal.pdf")
    res = export_html_to_pdf(test_in, test_out)
    print("PDF Exporter output:", res)
