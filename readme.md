## Invoice Processing Demo

This project is a Streamlit application that demonstrates how to ingest an invoice, parse the invoice pdf with Azure Document Intelligence, and extract structured data from the parsed markdown with a language model.

### Setup

- Install dependencies: `poetry install`
- Set the required environment variables for Azure Document Intelligence and OpenAI in a `.env` file.

### Run the App

- Launch the Streamlit interface: `poetry run streamlit run app.py`
- Upload an invoice (PDF or image) to see the parsed data and structured output.

### Project Structure

- `app.py`: Streamlit UI entrypoint.
- `src/ocr/azure_doc_parser.py`: Handles OCR via Azure.
- `src/chains/process_invoice_chain.py`: Orchestrates LLM processing.
- `src/prompts/process_invoice_prompt.py`: Prompt templates for the LLM.
- `src/parsers/process_invoice_parser.py`: Parses LLM responses.

### Notes

- Update prompts or parsing logic to tailor the app to different invoice output required.
