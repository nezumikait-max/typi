import config
from google.genai import types

def clean_filler(text: str) -> str:
    """
    Cleans up common Gemini conversational filler and markdown code blocks.
    Ensures that only the pure, refined text is returned.
    """
    if not text:
        return text

    text = text.strip()

    # 1. Strip markdown code block wrappers
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            # Check if first line is a language tag (e.g., ```email) and strip it
            text = "\n".join(lines[1:-1]).strip()

    # 2. Strip common introductory preambles (case-insensitive)
    filler_headers = [
        "here is the rewritten text:",
        "here is the polished text:",
        "here is the corrected text:",
        "here is the email:",
        "here is the professional rewrite:",
        "here is a professional rewrite:",
        "here is the rewritten email:",
        "rewritten text:",
        "corrected version:",
        "polished version:",
        "here is the casual version:",
        "here is the expanded version:",
        "subject:"
    ]

    text_lower = text.lower()
    for header in filler_headers:
        if text_lower.startswith(header):
            text = text[len(header):].strip()
            
            # If the output text was wrapped in quotes, strip them
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1].strip()
            elif text.startswith("'") and text.endswith("'"):
                text = text[1:-1].strip()
            break

    return text

def process_text(text: str, system_instruction: str) -> str:
    """
    Processes the input text using Gemini 2.5 Flash with a custom system instruction.
    Fixes or refines the text according to the specific trigger prompt.
    If an error occurs, it returns the original text to prevent data loss.
    """
    if not text or not text.strip():
        return text

    try:
        from google import genai
        
        api_key = config.get_api_key()
        client = genai.Client(api_key=api_key)
        
        # Inject strict formatting constraints to the instruction
        full_instruction = (
            f"{system_instruction}\n\n"
            "CRITICAL FORMATTING CONSTRAINTS:\n"
            "1. Output ONLY the polished/rewritten text. Do NOT include any introductory or concluding comments.\n"
            "2. Do NOT provide explanations, commentaries, or editing logs.\n"
            "3. Do NOT wrap your output in markdown code blocks (e.g., do not use ```).\n"
            "4. Preserve the formatting and language of the input."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=full_instruction,
                temperature=0.3,
            )
        )
        
        result = response.text
        if result:
            return clean_filler(result)
            
        return text
        
    except Exception as e:
        print(f"\n[AI Engine Error]: {str(e)}")
        return text
