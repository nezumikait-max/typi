import sys
import time

# Force UTF-8 encoding for standard output and error to support unicode emojis on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import keyboard
import pyperclip
import ai_engine

# Dictionary of available triggers and their respective AI roles/prompts
TRIGGERS = {
    "!fix": {
        "action_name": "Fix Grammar & Typos",
        "system_prompt": (
            "You are a helpful writing assistant. Correct all typos, grammar errors, "
            "spelling mistakes, and punctuation issues in the text. Improve flow and clarity. "
            "Return ONLY the corrected sentence or paragraph. Do not include introductory comments, "
            "markdown blocks, or explanation."
        )
    },
    "!email": {
        "action_name": "Rewrite as Professional Email",
        "system_prompt": (
            "You are a professional business writer. Rewrite the input text into a clear, "
            "polite, professional, and well-structured business email. "
            "Return ONLY the email body itself. Do not include subject line placeholders, "
            "greetings like 'Here is your email', or markdown code blocks."
        )
    },
    "!casual": {
        "action_name": "Rewrite in Casual Tone",
        "system_prompt": (
            "You are a friendly writing assistant. Rewrite the input text in a warm, "
            "relaxed, friendly, and casual conversational tone. "
            "Return ONLY the casual rewrite. Do not include commentary or markdown blocks."
        )
    },
    "!expand": {
        "action_name": "Expand Details & Paragraphs",
        "system_prompt": (
            "You are an expert editor. Elaborate on the user's input text. Flesh out the details, "
            "expand it into a complete, well-formed, logical paragraph or message. "
            "Return ONLY the expanded text without any introductory remarks or markdown blocks."
        )
    }
}

# State variables for the rolling key log
typed_buffer = []
processing_state = False

def process_trigger_immediately(trigger):
    """
    Triggers when an inline command is detected at the end of a typed buffer.
    Removes the trigger from the screen, selects the preceding line content,
    submits it to Gemini, and overwrites the text.
    """
    global processing_state
    
    processing_state = True
    # Unhook the key listener to prevent simulated keypresses from entering the buffer
    keyboard.unhook_all()
    
    original_clipboard = None
    try:
        # Step 1: Send backspaces to delete the trigger from the screen (e.g. 6 backspaces for !email)
        trigger_len = len(trigger)
        print(f"\n🔴 [Typi] Trigger '{trigger}' detected. Erasing trigger...")
        for _ in range(trigger_len):
            keyboard.send('backspace')
            time.sleep(0.005)
            
        time.sleep(0.05)
        
        # Backup the current clipboard
        original_clipboard = pyperclip.paste()
        pyperclip.copy("")
        
        # Step 2: Highlight the preceding text on the current line
        # We simulate Shift+Home to select from current cursor position back to start of the line
        keyboard.press('shift')
        keyboard.send('home')
        keyboard.release('shift')
        time.sleep(0.10)
        
        # Copy the selected text to clipboard
        keyboard.press_and_release('ctrl+c')
        time.sleep(0.10)
        
        captured_text = pyperclip.paste()
        
        # If nothing was selected or text is empty, cancel operation and deselect
        if not captured_text or not captured_text.strip():
            print("⚠️ [Typi] No preceding text on the current line. Aborting.")
            keyboard.send('right')  # Press Right arrow to deselect
            if original_clipboard is not None:
                pyperclip.copy(original_clipboard)
            return
            
        # Clean text
        text_to_process = captured_text.strip()
        print(f"📖 [Typi] Captured text: \"{text_to_process[:40]}...\"")
        
        # Step 3: Call Gemini AI engine
        prompt_info = TRIGGERS[trigger]
        print(f"🤖 [Typi] Refinement role: {prompt_info['action_name']}...")
        
        polished_text = ai_engine.process_text(text_to_process, prompt_info['system_prompt'])
        
        # Step 4: Overwrite selected text if changes were made
        if not polished_text or polished_text == text_to_process:
            print("✨ [Typi] Text is already optimal. Deselecting.")
            keyboard.send('right')  # Deselect
        else:
            pyperclip.copy(polished_text)
            print("✍️ [Typi] Pasting polished text...")
            keyboard.press_and_release('ctrl+v')
            time.sleep(0.10)
            print("🎉 [Typi] Text successfully refined!")
            
    except Exception as e:
        print(f"❌ [Typi Error] Replacement failed: {str(e)}")
        # Move cursor to right to deselect in case of failure
        keyboard.send('right')
        
    finally:
        # Restore the original clipboard backup
        if original_clipboard is not None:
            try:
                pyperclip.copy(original_clipboard)
            except:
                pass
                
        # Re-register the key listener hook
        processing_state = False
        keyboard.hook(on_key_event)
        print("🌀 [Typi] Standing by for triggers...")

def on_key_event(event):
    """
    Hooked key listener callback. Monitors typed characters, keeps a rolling buffer,
    and intercepts triggers at the end of the text.
    """
    global typed_buffer, processing_state
    
    # Process key down events only
    if event.event_type == 'down':
        key_name = event.name
        print(f"Captured key: '{key_name}'", flush=True)
        
        # Ignore modifier keys so they don't break character tracking
        if key_name in ['shift', 'ctrl', 'alt', 'windows', 'caps lock', 'num lock', 'scroll lock']:
            return
            
        # Clear rolling buffer on cursor navigation to reset tracking focus
        if key_name in ['left', 'right', 'up', 'down', 'esc', 'tab', 'home', 'end', 'page up', 'page down']:
            typed_buffer.clear()
            return
            
        # Handle Backspace
        if key_name == 'backspace':
            if typed_buffer:
                typed_buffer.pop()
            return
            
        # Translate special key names to strings
        if key_name == 'space':
            char = " "
        elif key_name == 'enter':
            char = "\n"
        elif len(key_name) == 1:
            char = key_name
        else:
            return  # Ignore other functional buttons (F1-F12, print screen, etc.)
            
        # Append to our rolling log of typed characters
        typed_buffer.append(char)
        if len(typed_buffer) > 20:
            typed_buffer.pop(0)
            
        current_str = "".join(typed_buffer).lower()
        
        # Check if the buffer ends with any trigger
        for trigger in TRIGGERS.keys():
            if current_str.endswith(trigger):
                typed_buffer.clear()
                process_trigger_immediately(trigger)
                break

def main():
    print("=" * 70)
    print("🌀 Typi AI Writing Assistant Daemon (Post-Fix Triggers)")
    print("=" * 70)
    print("Status: Active and running in the background.")
    print("Usage:")
    print("  Write your text and append a trigger at the end to activate.")
    print("  Example: send me report by eod !email")
    print("Triggers:")
    print("  - !fix    : Fix grammar and typos")
    print("  - !email  : Rewrite as a professional business email")
    print("  - !casual : Rewrite in warm, casual tone")
    print("  - !expand : Expand details into full paragraphs")
    print("Press [ Ctrl + C ] in this terminal window to exit.")
    print("-" * 70)
    print("🌀 [Typi] Standing by for triggers...")
    
    # Start hook listening
    keyboard.hook(on_key_event)
    
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n👋 [Typi] Daemon shut down gracefully. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
