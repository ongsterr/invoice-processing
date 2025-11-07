from src.ocr import parse_pdf_azure
from src.chains import process_invoice_chain


def process_invoice(invoice_filepath):
    print(f"Processing invoice from {invoice_filepath}")
    pdf_output = parse_pdf_azure(pdf_path=invoice_filepath)
    pdf_markdown = pdf_output["doc_content"]

    print(f"Extracting invoice data from invoice markdown")
    invoice_output = process_invoice_chain(invoice_details=pdf_markdown)
    print(f"Invoice data extracted successfully")
    print(f"Invoice data: {invoice_output}")
    return invoice_output


if __name__ == "__main__":
    invoice_filepath = "./data/vietnam_test_invoice2.pdf"

    invoice_output = process_invoice(invoice_filepath)
