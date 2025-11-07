import requests
import tempfile
from pathlib import Path


def download_pdf(url: str) -> Path:
    """Download PDF from URL to temporary file."""
    response = requests.get(url)
    response.raise_for_status()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(response.content)
    temp_file.close()

    return Path(temp_file.name)
