import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from mpxpy.mathpix_client import MathpixClient

# Configure module logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Load credentials from .env
load_dotenv()
APP_ID = os.getenv("MATHPIX_APP_ID")
APP_KEY = os.getenv("MATHPIX_APP_KEY")


def ingest_pdf(pdf_path: str) -> str:
    """
    Upload a PDF to MathPix, wait for processing, and return Markdown output.

    This function uses the `mpxpy` Mathpix client to submit a PDF job
    (equivalent to the MathPix `/v3/pdf` endpoint), blocks until the
    job completes, and returns the extracted Markdown representation of
    the document.

    Args:
        pdf_path: Path to the local PDF file to ingest.

    Returns:
        The extracted document as a Markdown-formatted string.

    Raises:
        RuntimeError: If MathPix credentials are not available in the
            environment or if the job fails.

    Notes:
        - Ensure `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` are exported in
          your environment (or provided via a .env file loaded by
          `python-dotenv`).
        - The function requests Markdown conversion via
          `convert_to_md=True` and disables DOCX output.
    """

    # Validate environment variables
    if not APP_ID or not APP_KEY:
        raise RuntimeError(
            "MATHPIX_APP_ID and MATHPIX_APP_KEY must be set in environment."
        )

    if not pdf_path:
        raise RuntimeError("PDF file path is required")

    # Create new client
    client = MathpixClient(app_id=APP_ID, app_key=APP_KEY)

    # Submit PDF job
    pdf = client.pdf_new(
        file_path=pdf_path,
        convert_to_md=True,
        convert_to_docx=False,
    )
    logger.info("[Mathpix] PDF job submitted: %s", pdf_path)

    # Poll until processing is finished
    logger.info("[Mathpix] Waiting for PDF processing to complete...")
    pdf.wait_until_complete()
    logger.info("[Mathpix] PDF processing completed.")

    # Retrieve Markdown
    logger.info("[Mathpix] Retrieving extracted Markdown...")
    md_text = pdf.to_md_text()
    logger.info("[Mathpix] Markdown retrieval completed.")
    return md_text


if __name__ == "__main__":
    if Path("texts/text.txt").exists():
        logger.error("texts/text.txt already exists — skipping ingestion.")
        exit(1)
    extracted_text = ingest_pdf("pdfs/algebra-trig.pdf")

    # Save extracted text to `texts/text.txt` if it doesn't already exist
    if extracted_text:
        out_dir = Path("texts")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "text.txt"
        if not out_file.exists():
            out_file.write_text(extracted_text, encoding="utf-8")
            logger.info("Saved extracted text to %s", out_file)
        else:
            logger.warning("File %s already exists — skipping write.", out_file)
    else:
        logger.error("No extracted text to save.")
