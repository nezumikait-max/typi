import config
from google.genai import types

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
            result = result.strip()
            # Post-processing fallback: remove code blocks if the model ignored instructions
            if result.startswith("```") and result.endswith("```"):
                lines = result.splitlines()
                if len(lines) >= 3:
                    result = "\n".join(lines[1:-1]).strip()
            return result
            
        return text
        
    except Exception as e:
        print(f"\n[AI Engine Error]: {str(e)}")
        return text
