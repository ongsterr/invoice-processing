from langchain_openai import AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv()


def load_llm_models(model: str):
    """
    Load an LLM model based on the provided model ID.

    Args:
        model: The ID of the model to load.

    Returns:
        The loaded LLM model.
    """

    if model == "azure-gpt-4o":
        llm = AzureChatOpenAI(
            azure_deployment="gpt-4o",
            azure_endpoint="https://construct-llm.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview",
            api_version="2024-08-01-preview",
            temperature=0,
            max_tokens=16384,
            timeout=240,
        )

    elif model == "azure-gpt-4.1-mini":
        llm = AzureChatOpenAI(
            azure_deployment="gpt-4.1-mini",
            azure_endpoint="https://chris-m5tp6zj5-eastus2.cognitiveservices.azure.com/",
            api_version="2024-12-01-preview",
            temperature=0,
            max_tokens=16384,
            timeout=240,
        )

    elif model == "azure-gpt-4.1":
        llm = AzureChatOpenAI(
            azure_deployment="gpt-4.1-parsetron",
            azure_endpoint="https://parsetron.openai.azure.com/openai/deployments/gpt-4.1-parsetron/chat/completions?api-version=2025-01-01-preview",
            api_version="2024-12-01-preview",
            temperature=0,
            timeout=240,
        )

    elif model == "azure-o4-mini":
        llm = AzureChatOpenAI(
            azure_deployment="o4-mini-parsetron",
            azure_endpoint="https://parsetron.openai.azure.com/openai/deployments/o4-mini-parsetron/chat/completions?api-version=2025-01-01-preview",
            api_version="2024-12-01-preview",
            temperature=1,
            timeout=240,
        )

    elif model == "azure-o3":
        llm = AzureChatOpenAI(
            azure_deployment="o3-parsetron",
            azure_endpoint="https://parsetron.openai.azure.com/openai/deployments/o3-parsetron/chat/completions?api-version=2025-01-01-preview",
            api_version="2024-12-01-preview",
            temperature=1,
            timeout=240,
        )

    elif model == "azure-gpt-5":
        llm = AzureChatOpenAI(
            azure_deployment="gpt-5-parsetron",
            azure_endpoint="https://parsetron.openai.azure.com/openai/deployments/gpt-5-parsetron/chat/completions?api-version=2025-01-01-preview",
            api_version="2024-12-01-preview",
            temperature=1,
            timeout=240,
        )

    elif model == "claude-3-5-sonnet":
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-latest",
            temperature=0,
            max_tokens=8192,
            timeout=240,
        )

    elif model == "claude-3-7-sonnet":
        llm = ChatAnthropic(
            model="claude-3-7-sonnet-latest",
            temperature=0,
            max_tokens=64000,
            timeout=240,
        )

    elif model == "gemini-2.0-flash":
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=32000,
            timeout=240,
        )

    elif model == "gemini-2.5-flash":
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            max_tokens=65000,
            timeout=240,
        )

    elif model == "gemini-2.5-pro":
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0,
            max_tokens=65000,
            timeout=300,
        )

    return llm
