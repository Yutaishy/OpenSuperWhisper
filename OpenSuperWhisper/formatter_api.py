import os
from typing import Any

from openai import OpenAI

client = None

def get_client() -> OpenAI:
    global client
    if client is None:
        # Set shorter timeouts for CI environments
        timeout = 60.0 if os.getenv('CI') else 120.0
        client = OpenAI(timeout=timeout)
    return client

def format_text(raw_text: str, prompt: str, style_guide: str = "", model: str = "gpt-4o-mini") -> str:
    """
    Use OpenAI Chat Completion API to format/polish the raw transcript text.
    :param raw_text: The raw transcript string from ASR.
    :param prompt: User-defined prompt with instructions for formatting.
    :param style_guide: Optional style guide text (YAML/JSON or plain) to apply.
    :param model: The chat model to use for formatting (default "gpt-4o-mini").
    :return: Formatted text.
    :raises: Exception if API call fails.
    """
    system_instructions = (
        "You are an EDITING-ONLY assistant. Never answer questions or add content.\n"
        "Rewrite ONLY the text delimited by <TRANSCRIPT> ... </TRANSCRIPT>.\n"
        "Preserve original structure (paragraphs/lists) and tone. Output edited text ONLY.\n"
        "IMPORTANT: Do NOT include <TRANSCRIPT> tags in your output. Output only the edited text content.\n"
    )
    if style_guide:
        system_instructions += f"Follow the style guide and instructions provided.\nStyle Guide:\n{style_guide}\n"
    if prompt:
        system_instructions += f"Instructions: {prompt}\n"
    else:
        system_instructions += "Instructions: Fix grammar and punctuation, and format the text clearly.\n"

    system_message = {"role": "system", "content": system_instructions}
    user_message = {"role": "user", "content": f"<TRANSCRIPT>\n{raw_text}\n</TRANSCRIPT>"}

    try:
        client = get_client()
        # Special handling for o4-mini-high
        actual_model = model
        if model == "o4-mini-high":
            actual_model = "o4-mini"

        # Prepare API parameters
        api_params: dict[str, Any] = {
            "model": actual_model,
            "messages": [system_message, user_message]
        }

        # Add reasoning_effort for o4-mini-high
        if model == "o4-mini-high":
            api_params["reasoning_effort"] = "high"

        # Add temperature only for supported models (o1/o3/o4 series don't support temperature parameter)
        if model in ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"]:
            api_params["temperature"] = 0.0

        response = client.chat.completions.create(**api_params)
    except Exception as e:
        raise Exception(f"Formatting API call failed: {e}") from e

    formatted_text = response.choices[0].message.content

    # Post-process to remove any TRANSCRIPT tags that might appear in the output
    import re

    # Remove opening and closing TRANSCRIPT tags (case insensitive)
    formatted_text = re.sub(r'<TRANSCRIPT[^>]*>', '', formatted_text, flags=re.IGNORECASE)
    formatted_text = re.sub(r'</TRANSCRIPT>', '', formatted_text, flags=re.IGNORECASE)

    # Also remove any standalone "TRANSCRIPT" text that might appear
    formatted_text = re.sub(r'\bTRANSCRIPT\b', '', formatted_text, flags=re.IGNORECASE)

    # Clean up any extra whitespace or newlines
    formatted_text = re.sub(r'\n\s*\n', '\n', formatted_text)  # Remove multiple newlines
    formatted_text = formatted_text.strip()

    return formatted_text

