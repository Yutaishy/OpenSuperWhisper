from openai import OpenAI
from .prompt_manager import PromptManager

client = None

def get_client():
    global client
    if client is None:
        client = OpenAI()
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
    system_instructions = "You are an assistant that formats and edits transcribed text.\n"
    if style_guide:
        system_instructions += f"Follow the style guide and instructions provided.\nStyle Guide:\n{style_guide}\n"
    if prompt:
        system_instructions += f"Instructions: {prompt}\n"
    else:
        system_instructions += "Instructions: Fix grammar and punctuation, and format the text clearly.\n"
    
    system_message = {"role": "system", "content": system_instructions}
    user_message = {"role": "user", "content": raw_text}
    
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=model,
            messages=[system_message, user_message]
        )
    except Exception as e:
        raise Exception(f"Formatting API call failed: {e}")
    
    formatted_text = response.choices[0].message.content
    return formatted_text.strip()

def format_text_with_manager(raw_text: str, prompt_manager: PromptManager, model: str = "gpt-4o-mini") -> str:
    """
    Use PromptManager to format text with managed prompt and style guide.
    :param raw_text: The raw transcript string from ASR.
    :param prompt_manager: PromptManager instance with loaded prompt and style guide.
    :param model: The chat model to use for formatting.
    :return: Formatted text.
    :raises: Exception if API call fails.
    """
    system_instructions = prompt_manager.get_combined_instructions()
    system_message = {"role": "system", "content": system_instructions}
    user_message = {"role": "user", "content": raw_text}
    
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=model,
            messages=[system_message, user_message]
        )
    except Exception as e:
        raise Exception(f"Formatting API call failed: {e}")
    
    formatted_text = response.choices[0].message.content
    return formatted_text.strip()