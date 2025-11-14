import csv
import pandas as pd
import tempfile
from io import BytesIO
from pathlib import Path
import os

import streamlit as st
from dotenv import load_dotenv

from src.chains import process_invoice_chain
from src.ocr import parse_pdf_azure


load_dotenv()

APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

DEFAULT_CREDENTIALS: dict[str, str] = {APP_USERNAME: APP_PASSWORD}


def load_credentials() -> dict[str, str]:
    """Return a username/password mapping, merging defaults with Streamlit secrets if present."""
    credentials = DEFAULT_CREDENTIALS.copy()
    try:
        secrets_credentials = dict(st.secrets["credentials"])
    except Exception:  # pragma: no cover - depends on deployment configuration
        secrets_credentials = {}
    credentials.update(secrets_credentials)
    return credentials


def require_login() -> None:
    """Render a simple login form and stop execution until the user is authenticated."""
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("auth_error", "")

    if st.session_state.authenticated:
        username = st.session_state.get("username", "")
        with st.sidebar:
            st.success(f"Logged in as {username}")
            if st.button("Log out"):
                st.session_state.authenticated = False
                st.session_state.username = ""
                st.rerun()
        return

    st.markdown("#### **Login Required**")
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        credentials = load_credentials()
        if credentials.get(username) == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.auth_error = ""
            st.rerun()
        else:
            st.session_state.auth_error = "Invalid username or password."

    if st.session_state.auth_error:
        st.error(st.session_state.auth_error)

    st.stop()


def flatten_invoice_output(invoice_content: dict) -> list[dict]:
    """Flatten nested invoice output for CSV export."""

    def _flatten_dict(data: dict, parent_key: str = "", sep: str = "_") -> dict:
        flat: dict[str, object] = {}
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                flat.update(_flatten_dict(value, new_key, sep=sep))
            else:
                flat[new_key] = value
        return flat

    base_keys = {k: v for k, v in invoice_content.items() if k != "items"}
    base_flat = _flatten_dict(base_keys)
    items = invoice_content.get("items") or []

    if not items:
        return [base_flat] if base_flat else []

    flattened_rows: list[dict] = []
    for item in items:
        item_flat = _flatten_dict(item or {}, parent_key="item")
        row = base_flat | item_flat
        flattened_rows.append(row)

    return flattened_rows


def render_pdf_viewer(pdf_bytes: bytes, *, height: int = 600) -> None:
    """Display uploaded PDF in the Streamlit app."""

    pdf_buffer = BytesIO(pdf_bytes)
    pdf_buffer.seek(0)
    st.pdf(pdf_buffer, height=height)


st.set_page_config(page_title="Invoice Processing", layout="centered")
st.title("Invoice Processing Demo")

require_login()

st.markdown(
    """
    1. Upload an invoice PDF
    2. Key data points from the invoice will be extracted and displayed in a structured format
    3. The extracted data can be downloaded as a CSV file
    """
)


uploaded_file = st.file_uploader("Upload invoice PDF", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.getvalue()

    st.markdown("#### **Invoice PDF Preview**")
    render_pdf_viewer(pdf_bytes)

    process_clicked = st.button("Extract Invoice Data", type="primary")

    if process_clicked:
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_bytes)
                temp_path = Path(temp_file.name)

            with st.spinner("Convert PDF to markdown text..."):
                pdf_output = parse_pdf_azure(pdf_path=str(temp_path))
                pdf_pages = len(pdf_output["doc_pages"])

            if not pdf_output:
                st.error("Unable to parse the uploaded PDF. Please try another file.")
            else:
                markdown_content = pdf_output["doc_content"]

                with st.expander("Text View"):
                    st.markdown(markdown_content, unsafe_allow_html=True)

                with st.spinner("Extracting structured invoice data..."):
                    invoice_result = process_invoice_chain(invoice_details=markdown_content)

                invoice_data = invoice_result.get("content") or {}

                with st.expander("Form View", expanded=True):
                    confidence_level = invoice_data.get("metadata", {}).get("confidence_score", "")
                    if confidence_level < 0.6:
                        st.error(f"Invoice Processed with Low Confidence ({confidence_level})", icon="🔴")
                    elif confidence_level < 0.9:
                        st.info(f"Invoice Processed with Medium Confidence ({confidence_level})", icon="🟡")
                    else:
                        st.success(f"Invoice Processed with High Confidence ({confidence_level})", icon="🟢")

                    form_col1, form_col2 = st.columns(2)
                    with form_col1:
                        st.text_input(
                            "Invoice ID",
                            value=str(invoice_data.get("invoice_id", "")),
                            disabled=False,
                        )
                        st.text_input(
                            "Invoice Total",
                            value=str(invoice_data.get("invoice_total", "")),
                            disabled=False,
                        )
                        st.text_input(
                            "Seller Name",
                            value=str(invoice_data.get("seller_name", "")),
                            disabled=False,
                        )
                    with form_col2:
                        st.text_input(
                            "Invoice Language",
                            value=str(invoice_data.get("metadata", {}).get("language", "")),
                            disabled=False,
                        )
                        st.text_input(
                            "Invoice Date",
                            value=str(invoice_data.get("invoice_date", "")),
                            disabled=False,
                        )
                        st.text_input(
                            "Invoice Currency",
                            value=str(invoice_data.get("invoice_total_currency", "")),
                            disabled=False,
                        )

                    items = invoice_data.get("items") or []
                    if items:
                        item_rows = []
                        for item in items:
                            if not isinstance(item, dict):
                                continue
                            item_rows.append(
                                {
                                    "Cost Center": item.get("cost_center", ""),
                                    "Description": item.get("description", ""),
                                    "Qty": f"{item.get('quantity', 0):,.0f}" if item.get("quantity", 0) else None,
                                    "Unit $": f"{item.get('unit_price', 0):,.2f}" if item.get("unit_price", 0) else None,
                                    "Subtotal $": f"{item.get('subtotal_price', 0):,.2f}" if item.get("subtotal_price", 0) else None,
                                    "VAT $": f"{item.get('vat_amount', 0):,.2f}" if item.get("vat_amount", 0) else None,
                                    "Total $": f"{item.get('total_price', 0):,.2f}" if item.get("total_price", 0) else None,
                                }
                            )
                        if item_rows:
                            st.markdown("**Line Items**")
                            df_item_rows = pd.DataFrame(item_rows)
                            st.dataframe(df_item_rows, hide_index=True)
                        else:
                            st.info("No line item details available.")
                    else:
                        st.info("No line item details available.")

                with st.expander("Structured View"):
                    st.json(invoice_data)

                usage_metadata = invoice_result.get("usage_metadata")
                if usage_metadata:
                    with st.expander("Cost Summary"):
                        usage_metadata["ocr_cost_usd"] = round(pdf_pages * 190 / 20000, 6)
                        usage_metadata["total_cost_usd"] = usage_metadata["ocr_cost_usd"] + usage_metadata["llm_cost_usd"]
                        st.json(usage_metadata)

        except Exception as exc:  # pragma: no cover - Streamlit handles runtime errors
            st.error(f"An error occurred while processing the invoice: {exc}")
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)
