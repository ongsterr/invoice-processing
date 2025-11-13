from src.prompts.base_prompt import generate_prompt


def process_invoice_prompt():
    system_prompt = """
    You are a professional invoice processing specialist.
    """
    human_prompt = """
    <role>
    You are a professional invoice processing specialist.
    </role>

    <context>
    - You will be provided with a B2B invoice originally in PDF format but parsed into a markdown format in the invoice_details section.
    </context>

    <instructions>
    1. Identify the language the invoice is in. If the invoice is not in English, translate it into English.
    2. Study the structure of the invoice and identify the key sections.
    3. Extract the data points from the invoice based on the output_format provided.
    4. If the data points are not found, return None for that data point.
    5. If the data points are not clear or value confidence level is less than 0.8, return None for that data point.
    6. Only return the JSON output format, no other text or comments.
    </instructions>

    <output_format>
    Provide JSON in this exact structure:
    {{
        "invoice_id": <string>,
        "invoice_date": <string>,
        "invoice_total": <float>, # this is the total price after VAT
        "invoice_total_currency": <string>,
        "invoice_vat_amount": <float>,
        "invoice_vat_rate": <float>, # in decimal format i.e. 0.10 for 10%
        "buyer_name": <string>,
        "buyer_address": {{
            "street": <string>,
            "city": <string>,
            "state": <string>,
            "postcode": <string>,
            "country": <string>, # in 2 character ISO code
        }},
        "buyer_details": {{
            "name": <string>,
            "email": <string>,
            "phone": <string>,
        }},
        "buyer_contact_name": <string>,
        "seller_name": <string>,
        "seller_address": {{
            "street": <string>,
            "city": <string>,
            "state": <string>,
            "postcode": <string>,
            "country": <string>, # in 2 character ISO code
        }},
        "seller_details": {{
            "name": <string>,
            "email": <string>,
            "phone": <string>,
        }},
        "seller_contact_name": <string>,
        "items": [
            {{
                "cost_center": <string>, # this refers to the cost center which the item is charged to
                "description": <string>, # translate to english where possible
                "quantity": <float>,
                "unit_price": <float>,
                "subtotal_price": <float>, # this is the price before VAT
                "total_price": <float>, # this is the price after VAT
                "vat_rate": <float>,
                "vat_amount": <float>,
                "currency": <string>,
            }}
        ]
    }}
    </output_format>

    <example>
    {{
        "invoice_id": "1234567890",
        "invoice_date": "2025-01-01",
        "invoice_total": 100.00,
        "invoice_total_currency": "USD",
        "invoice_vat_amount": 10.00,
        "invoice_vat_rate": 0.10,
        "buyer_name": "Buyer Name",
        "buyer_address": {{
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postcode": "12345",
            "country": "US",
        }},
        "buyer_details": {{
            "name": "Buyer Name",
            "email": "buyer@example.com",
            "phone": "+11234567890", # include country code and phone number without space and special characters
        }},
        "buyer_contact_name": "Buyer Contact Name",
        "seller_name": "Seller Name",
        "seller_address": {{
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postcode": "12345",
            "country": "US",
        }},
        "seller_details": {{
            "name": "Seller Name",
            "email": "seller@example.com",
            "phone": "+11234567890", # include country code and phone number without space and special characters
        }},
        "seller_contact_name": "Seller Contact Name",
        "items": [
            {{
                "cost_center": "1234567890",
                "description": "Item Description",
                "quantity": 1.00,
                "unit_price": 100.00,
                "subtotal_price": 100.00,
                "vat_rate": 0.10,
                "vat_amount": 10.00,
                "total_price": 110.00,
                "currency": "USD",
            }}
        ]
    }}
    </example>

    <invoice_details format="markdown">
    {invoice_details}
    </invoice_details>
    """

    prompt = generate_prompt(system_prompt, human_prompt)

    return prompt
