import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationError


class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None


class PartyDetails(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class InvoiceItem(BaseModel):
    cost_center: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    subtotal_price: Optional[float] = None
    total_price: Optional[float] = None
    vat_rate: Optional[float] = None
    vat_amount: Optional[float] = None
    currency: Optional[str] = None


class ProcessInvoiceResult(BaseModel):
    invoice_id: Optional[str] = None
    invoice_date: Optional[str] = None
    invoice_total: Optional[float] = None
    invoice_total_currency: Optional[str] = None
    invoice_vat_amount: Optional[float] = None
    invoice_vat_rate: Optional[float] = None
    buyer_name: Optional[str] = None
    buyer_address: Address = Field(default_factory=Address)
    buyer_details: PartyDetails = Field(default_factory=PartyDetails)
    buyer_contact_name: Optional[str] = None
    seller_name: Optional[str] = None
    seller_address: Address = Field(default_factory=Address)
    seller_details: PartyDetails = Field(default_factory=PartyDetails)
    seller_contact_name: Optional[str] = None
    items: List[InvoiceItem] = Field(default_factory=list)


def parse_process_invoice_result(payload: Union[str, Dict[str, Any]]) -> ProcessInvoiceResult:
    if isinstance(payload, str):
        payload = json.loads(payload)

    try:
        return ProcessInvoiceResult.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Invalid process invoice result: {exc}") from exc
