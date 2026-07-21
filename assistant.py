import sys
import time

# Force UTF-8 encoding for standard output and error to support unicode emojis on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import keyboard
import ai_engine

# Dictionary of available triggers and their respective AI roles/prompts
TRIGGERS = {
    "!fix": {
        "action_name": "Fix Grammar & Typos",
        "system_prompt": (
            "You are a helpful writing assistant. Correct all typos, grammar errors, "
            "spelling mistakes, and punctuation issues in the text. Improve flow and clarity "
            "while maintaining the original tone and meaning."
        )
    },
    "!email": {
        "action_name": "Rewrite as Professional Email",
        "system_prompt": (
            "You are a professional business writer. Rewrite the input text into a clear, "
            "polite, professional, and well-structured business email."
        )
    },
    "!casual": {
        "action_name": "Rewrite in Casual Tone",
        "system_prompt": (
            "You are a friendly writing assistant. Rewrite the input text in a warm, "
            "relaxed, friendly, and casual conversational tone."
        )
    },
    "!expand": {
        "action_name": "Expand Details & Paragraphs",
        "system_prompt": (
            "You are an expert editor. Elaborate on the user's input text. Flesh out the details, "
            "expand it into a complete, well-formed, logical paragraph or message."
        )
    }
}

# State variables for the inline parser
active_trigger = None
captured_buffer = []
typed_buffer = []

# Concurrency state variables (handles user typing during Gemini processing)
processing_state = False
pending_typed_chars = []

def deactivate_and_replace():
    """
    Called when a deactivation trigger is detected.
    Signals the processing state, requests AI replacement, deletes triggers,
    injects polished text, and restores any text typed during the wait window.
    """
    global active_trigger, captured_buffer, typed_buffer, processing_state, pending_typed_chars
    
    trigger = active_trigger
    active_trigger = None
    typed_buffer.clear()
    
    # Extract the full string captured so far
    full_captured = "".join(captured_buffer)
    captured_buffer.clear()
    
    # Strip the deactivation trigger from the end of the text
    if not full_captured.endswith(trigger):
        print(f"⚠️ [Typi] Deactivation buffer misalignment. Aborting.")
        return
        
    text_to_process = full_captured[:-len(trigger)]
    
    if not text_to_process.strip():
        print("⚠️ [Typi] Captured text is empty. Skipping replacement.")
        return
        
    print(f"\n🔴 [Typi] Deactivation trigger detected for '{trigger}'.")
    print(f"📖 [Typi] Captured text: \"{text_to_process.strip()[:40]}...\"")
    print("🤖 [Typi] Calling AI engine (typing is unlocked during processing)...")
    
    # Enter processing state (we keep keyboard hooks active so user can type)
    processing_state = True
    pending_typed_chars.clear()
    
    # Fetch polished text from Gemini
    prompt_info = TRIGGERS[trigger]
    polished_text = None
    try:
        polished_text = ai_engine.process_text(text_to_process, prompt_info['system_prompt'])
    except Exception as e:
        print(f"⚠️ [Typi Error] Gemini lookup failed: {str(e)}")
        polished_text = text_to_process
        
    # Check if the user aborted the processing state (e.g. by moving the cursor)
    if not processing_state:
        print("⚠️ [Typi] Aborted replacement because the cursor position changed during processing.")
        return
        
    # Turn off processing state and temporarily unhook key listener to prevent simulated key capture
    processing_state = False
    keyboard.unhook_all()
    
    try:
        # Calculate backspaces required:
        # [Activation Trigger] + [Captured Text] + [Deactivation Trigger] + [User typing during processing]
        additional_text = "".join(pending_typed_chars)
        backspace_count = len(trigger) + len(text_to_process) + len(trigger) + len(additional_text)
        
        # Step 1: Send backspaces to delete everything up to the start of the activation trigger
        print(f"🧹 [Typi] Erasing text block ({backspace_count} characters)...")
        for _ in range(backspace_count):
            keyboard.send('backspace')
            time.sleep(0.005)
            
        time.sleep(0.05)
        
        # Step 2: Write the polished text
        print("✍️ [Typi] Writing polished text...")
        keyboard.write(polished_text)
        
        # Step 3: Re-type any characters the user typed during the processing delay
        if additional_text:
            print(f"✍️ [Typi] Restoring concurrently typed text: \"{additional_text}\"")
            keyboard.write(additional_text)
            
        print("🎉 [Typi] Text successfully refined!")
        
    except Exception as replacement_err:
        print(f"❌ [Typi Error] Replacement failed: {str(replacement_err)}")
        # Safety fallback: restore original text and additional typed text
        try:
            keyboard.write(text_to_process + additional_text)
        except:
            pass
            
    finally:
        # Re-register the key listener
        pending_typed_chars.clear()
        keyboard.hook(on_key_event)
        print("🌀 [Typi] Standing by for triggers...")

def on_key_event(event):
    """
    Hooked key listener callback. Monitors typed characters, keeps a rolling buffer,
    handles activation/deactivation, and logs typing during AI processing.
    """
    global active_trigger, captured_buffer, typed_buffer, processing_state, pending_typed_chars
    
    # Process key down events only
    if event.event_type == 'down':
        key_name = event.name
        
        # Cancel any active captures if the cursor is moved (Arrows, Mouse focus keys)
        if key_name in ['left', 'right', 'up', 'down', 'esc', 'tab', 'home', 'end', 'page up', 'page down']:
            if processing_state:
                processing_state = False  # Aborts replacement to avoid typing in wrong fields
            if active_trigger:
                print(f"⚠️ [Typi] Cursor movement detected ({key_name}). Resetting active trigger '{active_trigger}'.")
                active_trigger = None
                captured_buffer.clear()
            typed_buffer.clear()
            return
            
        # Ignore modifier keys so they don't break character tracking
        if key_name in ['shift', 'ctrl', 'alt', 'windows', 'caps lock', 'num lock', 'scroll lock']:
            return
            
        # Handle Backspace
        if key_name == 'backspace':
            if processing_state:
                if pending_typed_chars:
                    pending_typed_chars.pop()
                return
            if active_trigger:
                if captured_buffer:
                    captured_buffer.pop()
                else:
                    print(f"↩️ [Typi] Activation trigger '{active_trigger}' deleted. Resetting.")
                    active_trigger = None
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
            
        # If in processing state, log typing to restore it later
        if processing_state:
            pending_typed_chars.append(char)
            return
            
        # Accumulate captured text if in active mode
        if active_trigger:
            captured_buffer.append(char)
            
        # Keep a rolling buffer of recently typed characters
        typed_buffer.append(char)
        if len(typed_buffer) > 30:
            typed_buffer.pop(0)
            
        current_str = "".join(typed_buffer).lower()
        
        # Check triggers
        if active_trigger:
            if current_str.endswith(active_trigger):
                deactivate_and_replace()
        else:
            for trigger in TRIGGERS.keys():
                if current_str.endswith(trigger):
                    active_trigger = trigger
                    captured_buffer.clear()
                    typed_buffer.clear()
                    print(f"🟢 [Typi] Activation trigger '{trigger}' detected. Recording text...")
                    break

def main():
    print("=" * 70)
    print("🌀 Typi AI Writing Assistant Daemon (Inline Triggers)")
    print("=" * 70)
    print("Status: Active and running in the background.")
    print("Note: The keyboard is unlocked and fully responsive during processing.")
    print("Triggers:")
    print("  - !fix  ... !fix     : Fix grammar and typos")
    print("  - !email ... !email   : Rewrite into professional email")
    print("  - !casual ... !casual : Rewrite in warm, casual tone")
    print("  - !expand ... !expand : Expand details and construct paragraphs")
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
