from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage


def generate_prompt(system_prompt: str, human_prompt: str):
    """
    Generate a base prompt for the LLM.

    Args:
        system_prompt: The system prompt for the LLM.
        human_prompt: The human prompt for the LLM.
    """
    prompt_messages = [
        SystemMessage(content=system_prompt),
        HumanMessagePromptTemplate.from_template(
            template=[
                {"type": "text", "text": human_prompt},
            ]
        ),
    ]

    prompt_template = ChatPromptTemplate(messages=prompt_messages)

    return prompt_template
