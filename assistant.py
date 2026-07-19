import time
import sys
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

def deactivate_and_replace():
    """
    Called when a deactivation trigger is detected.
    Removes the triggers and text from the screen, refines it, and writes it back.
    """
    global active_trigger, captured_buffer, typed_buffer
    
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
    
    # Calculate backspaces required:
    # 1. Length of activation trigger (e.g., 4 characters for '!fix')
    # 2. Length of the captured text
    # 3. Length of deactivation trigger (e.g., 4 characters for '!fix')
    backspace_count = len(trigger) + len(text_to_process) + len(trigger)
    
    # Unhook keyboard events during simulation to prevent self-triggering feedback loops
    keyboard.unhook_all()
    
    try:
        # Step 1: Send backspaces to delete the triggers and raw text from the screen
        print(f"🧹 [Typi] Erasing triggers and raw text ({backspace_count} characters)...")
        for _ in range(backspace_count):
            keyboard.send('backspace')
            time.sleep(0.005)  # Tiny pause to ensure OS keystroke queue is not overloaded
            
        time.sleep(0.05)
        
        # Step 2: Query the Gemini API using the selected trigger prompt
        prompt_info = TRIGGERS[trigger]
        print(f"🤖 [Typi] Refinement role: {prompt_info['action_name']}...")
        
        polished_text = ai_engine.process_text(text_to_process, prompt_info['system_prompt'])
        
        # Step 3: Type the polished text back to the screen
        print("✍️ [Typi] Writing polished text...")
        keyboard.write(polished_text)
        print("🎉 [Typi] Text successfully refined!")
        
    except Exception as e:
        print(f"❌ [Typi Error] Replacement failed: {str(e)}")
        # Safety fallback: restore what the user typed in case of failure
        try:
            keyboard.write(text_to_process)
        except:
            pass
            
    finally:
        # Re-register the key listener
        keyboard.hook(on_key_event)
        print("🌀 [Typi] Standing by for triggers...")

def on_key_event(event):
    """
    Hooked key listener callback. Monitors typed characters, keeps a rolling buffer,
    and handles activation/deactivation triggers.
    """
    global active_trigger, captured_buffer, typed_buffer
    
    # Process key down events only
    if event.event_type == 'down':
        key_name = event.name
        
        # Cancel recording on any explicit cursor movement to prevent writing in wrong positions
        if key_name in ['left', 'right', 'up', 'down', 'esc', 'tab', 'home', 'end', 'page up', 'page down']:
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
            if active_trigger:
                if captured_buffer:
                    captured_buffer.pop()
                else:
                    # If they deleted past the text, they are deleting the activation trigger
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
            # Check for deactivation
            if current_str.endswith(active_trigger):
                deactivate_and_replace()
        else:
            # Check for activation
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
        # Keep main thread alive
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n👋 [Typi] Daemon shut down gracefully. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
