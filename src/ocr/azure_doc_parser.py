from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

from dotenv import load_dotenv
import os
from pathlib import Path
from urllib.parse import urlparse
from slugify import slugify

from src.utils import download_pdf


load_dotenv()


def parse_invoice_prebuilt(file_path: str = None, invoice_url: str = None) -> dict:
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # invoice_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/invoice_sample.jpg"
    file_bytes = Path(file_path).read_bytes()

    if file_path:
        poller = document_intelligence_client.begin_analyze_document("prebuilt-invoice", AnalyzeDocumentRequest(bytes_source=file_bytes))
    elif invoice_url:
        poller = document_intelligence_client.begin_analyze_document("prebuilt-invoice", AnalyzeDocumentRequest(url_source=invoice_url))
    invoices = poller.result()

    for idx, invoice in enumerate(invoices.documents):
        field = invoice.fields
        output = {
            "amount_due": field["AmountDue"]["valueCurrency"]["amount"] if field.get("AmountDue") else None,
            "amount_due_currency": field["AmountDue"]["valueCurrency"]["currencyCode"] if field.get("AmountDue") else None,
            "billing_address": field["BillingAddress"]["valueAddress"] if field.get("BillingAddress") else None,
            "billing_address_recipient": field["BillingAddressRecipient"]["valueString"] if field.get("BillingAddressRecipient") else None,
            "customer_address": field["CustomerAddress"]["valueAddress"] if field.get("CustomerAddress") else None,
            "customer_address_recipient": field["CustomerAddressRecipient"]["valueString"] if field.get("CustomerAddressRecipient") else None,
            "customer_id": field["CustomerId"]["valueString"] if field.get("CustomerId") else None,
            "customer_name": field["CustomerName"]["valueString"] if field.get("CustomerName") else None,
            "due_date": field["DueDate"]["valueDate"] if field.get("DueDate") else None,
            "invoice_date": field["InvoiceDate"]["valueDate"] if field.get("InvoiceDate") else None,
            "invoice_id": field["InvoiceId"]["valueString"] if field.get("InvoiceId") else None,
            "invoice_total": field["InvoiceTotal"]["valueCurrency"]["amount"] if field.get("InvoiceTotal") else None,
            "invoice_total_currency": field["InvoiceTotal"]["valueCurrency"]["currencyCode"] if field.get("InvoiceTotal") else None,
            "prev_unpaid_balance": field["PreviousUnpaidBalance"]["valueCurrency"]["amount"] if field.get("PreviousUnpaidBalance") else None,
            "prev_unpaid_balance_currency": field["PreviousUnpaidBalance"]["valueCurrency"]["currencyCode"] if field.get("PreviousUnpaidBalance") else None,
            "purchase_order": field["PurchaseOrder"]["valueString"] if field.get("PurchaseOrder") else None,
            "remittance_address": field["RemittanceAddress"]["valueAddress"] if field.get("RemittanceAddress") else None,
            "remittance_address_recipient": field["RemittanceAddressRecipient"]["valueString"] if field.get("RemittanceAddressRecipient") else None,
            "service_address": field["ServiceAddress"]["valueAddress"] if field.get("ServiceAddress") else None,
            "service_address_recipient": field["ServiceAddressRecipient"]["valueString"] if field.get("ServiceAddressRecipient") else None,
            "service_start_date": field["ServiceStartDate"]["valueDate"] if field.get("ServiceStartDate") else None,
            "service_end_date": field["ServiceEndDate"]["valueDate"] if field.get("ServiceEndDate") else None,
            "shipping_address": field["ShippingAddress"]["valueAddress"] if field.get("ShippingAddress") else None,
            "shipping_address_recipient": field["ShippingAddressRecipient"]["valueString"] if field.get("ShippingAddressRecipient") else None,
            "subtotal": field["SubTotal"]["valueCurrency"]["amount"] if field.get("SubTotal") else None,
            "subtotal_currency": field["SubTotal"]["valueCurrency"]["currencyCode"] if field.get("SubTotal") else None,
            "total_tax": field["TotalTax"]["valueCurrency"]["amount"] if field.get("TotalTax") else None,
            "total_tax_currency": field["TotalTax"]["valueCurrency"]["currencyCode"] if field.get("TotalTax") else None,
            "vendor_address": field["VendorAddress"]["valueAddress"] if field.get("VendorAddress") else None,
            "vendor_address_recipient": field["VendorAddressRecipient"]["valueString"] if field.get("VendorAddressRecipient") else None,
            "vendor_name": field["VendorName"]["valueString"] if field.get("VendorName") else None,
            "items": [
                {
                    "amount": item["valueObject"]["Amount"]["valueCurrency"]["amount"] if item["valueObject"].get("Amount") else None,
                    "amount_currency": item["valueObject"]["Amount"]["valueCurrency"]["currencyCode"] if item["valueObject"].get("Amount") else None,
                    "description": item["valueObject"]["Description"]["valueString"] if item["valueObject"].get("Description") else None,
                    "quantity": item["valueObject"]["Quantity"]["valueNumber"] if item["valueObject"].get("Quantity") else None,
                    "date": item["valueObject"]["Date"]["valueDate"] if item["valueObject"].get("Date") else None,
                }
                for item in field["Items"]["valueArray"]
            ],
        }

        return output


def parse_pdf_azure(pdf_url: str = None, pdf_path: str = None):
    """
    Parse PDF using Azure Document Intelligence and return content split by pages

    Args:
        pdf_url: URL of the PDF document
        pdf_title: Title of the PDF document

    Returns:
        List of dictionaries containing parsed content and metadata
    """
    if pdf_url and not pdf_path:
        print(f"Downloading PDF from URL: {pdf_url}")
        pdf_path = download_pdf(pdf_url)
        temp_file = True
    else:
        temp_file = False

    try:
        loader = AzureAIDocumentIntelligenceLoader(
            api_endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
            api_key=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"),
            url_path=pdf_url,
            file_path=pdf_path,
            api_model="prebuilt-layout",
            mode="markdown",
        )

        documents = loader.load()

        doc_pages_raw = documents[0].page_content.split("<!-- PageBreak -->")

        temp_dir = Path("data") / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        doc_slug_source: str | None = None
        if pdf_path:
            doc_slug_source = Path(pdf_path).stem
        elif pdf_url:
            parsed_url = urlparse(pdf_url)
            doc_slug_source = Path(parsed_url.path).stem or parsed_url.netloc

        if not doc_slug_source:
            print("No PDF path or URL provided")
            return None

        doc_slug = slugify(doc_slug_source) or "document"
        output_path = temp_dir / f"{doc_slug}.md"
        output_path.write_text(documents[0].page_content, encoding="utf-8")

        doc_pages = []
        for i, page in enumerate(doc_pages_raw, start=1):
            has_table = True if "<table>" in page else False
            has_lca = True if "<table>" in page and "gwp" in page.lower() else False
            doc_page = {
                "page": i,
                "has_table": has_table,
                "has_lca": has_lca,
                "source_url": pdf_url,
                "content": page,
            }
            doc_pages.append(doc_page)

        return {
            "doc_slug": doc_slug,
            "doc_pages": doc_pages,
            "doc_content": documents[0].page_content,
        }
    finally:
        # Clean up temporary file if we downloaded it
        if temp_file and pdf_path and Path(pdf_path).exists():
            Path(pdf_path).unlink()
