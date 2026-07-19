import config
from google.genai import types

def process_text(text: str) -> str:
    """
    Processes the input text using Gemini 2.5 Flash.
    Fixes grammar, typos, style, and flow, returning ONLY the polished result.
    If an error occurs, it returns the original text to prevent data loss.
    """
    if not text or not text.strip():
        return text

    try:
        # Import the SDK lazily to ensure startup is fast
        from google import genai
        
        api_key = config.get_api_key()
        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are a system-wide AI Writing Assistant. Your task is to rewrite, refine, and polish "
            "the user's highlighted text. Correct all typos, grammar errors, spelling mistakes, punctuation "
            "issues, and stylistic inconsistencies, making the flow smooth and professional.\n\n"
            "CRITICAL CONSTRAINTS:\n"
            "1. Output ONLY the polished and corrected text. Do NOT include any introductory or concluding comments.\n"
            "2. Do NOT provide explanations, commentaries, metadata, or edit logs.\n"
            "3. Do NOT wrap your output in markdown code blocks (e.g., do not use ```).\n"
            "4. Maintain the original formatting, line breaks, and language of the input.\n"
            "5. If the input is already clean and correct, output the exact input text unchanged."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,  # Low temperature for precise, deterministic corrections
            )
        )
        
        result = response.text
        if result:
            result = result.strip()
            # Post-processing fallback: remove markdown code blocks if the model ignored system instructions
            if result.startswith("```") and result.endswith("```"):
                lines = result.splitlines()
                if len(lines) >= 3:
                    # Strip standard markdown language header if present
                    result = "\n".join(lines[1:-1]).strip()
            return result
            
        return text
        
    except Exception as e:
        # Gracefully log the error and fallback to returning original text
        print(f"\n[AI Engine Error]: {str(e)}")
        return text
