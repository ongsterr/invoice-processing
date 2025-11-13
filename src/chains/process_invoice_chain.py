import json
import ast

from src.models import load_llm_models
from src.prompts import process_invoice_prompt
from src.parsers import parse_process_invoice_result


def return_json_result(result):
    if isinstance(result, dict):
        return result
    cleaned = result.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        python_obj = ast.literal_eval(cleaned)
        if isinstance(python_obj, dict):
            return python_obj
        raise ValueError("LLM response is not a JSON object")


def process_invoice_chain(invoice_details, model="azure-gpt-4.1"):
    prompt_template = process_invoice_prompt()
    llm = load_llm_models(model=model)
    chain = prompt_template | llm

    result = chain.invoke({"invoice_details": invoice_details})

    raw_content = return_json_result(result.content)
    parsed_content = parse_process_invoice_result(raw_content)
    parsed_content_dict = parsed_content.model_dump()

    result.usage_metadata["model"] = model

    input_tokens = result.usage_metadata["input_tokens"]
    output_tokens = result.usage_metadata["output_tokens"]
    result.usage_metadata["llm_cost_usd"] = round(input_tokens * 2.0 / 1000000 + output_tokens * 8.0 / 1000000, 6)
    result_output = {"content": parsed_content_dict, "usage_metadata": result.usage_metadata}
    return result_output
