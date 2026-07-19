import time
import sys
import keyboard
import pyperclip
import ai_engine

# Adjustable delays (in seconds) to prevent OS/application race conditions
KEY_RELEASE_DELAY = 0.05
CLIPBOARD_COPY_DELAY = 0.10
CLIPBOARD_PASTE_DELAY = 0.10

def trigger_writing_assistant():
    """
    Core handler triggered by the Ctrl+Alt+A hotkey.
    Captures highlighted text, refines it with Gemini, replaces it,
    and restores the user's clipboard history.
    """
    original_clipboard = None
    try:
        print("\n⚡ [Typi Assistant] Hotkey triggered! Capture initiated...")
        
        # Step 1: Backup current clipboard contents
        original_clipboard = pyperclip.paste()
        
        # Step 2: Clear clipboard to verify if a copy operation actually occurs
        pyperclip.copy("")
        
        # Step 3: Release hotkey modifier keys to avoid interference with simulated keys
        # If user is still holding Ctrl/Alt, the OS may register Ctrl+Alt+C instead of Ctrl+C
        keyboard.release('ctrl')
        keyboard.release('alt')
        keyboard.release('a')
        time.sleep(KEY_RELEASE_DELAY)
        
        # Step 4: Simulate Copy (Ctrl+C) to capture highlighted text
        keyboard.press_and_release('ctrl+c')
        time.sleep(CLIPBOARD_COPY_DELAY)
        
        # Step 5: Extract the captured text
        captured_text = pyperclip.paste()
        if not captured_text or not captured_text.strip():
            print("⚠️ [Typi Assistant] No text highlighted. Clipboard restoration complete. Skipping.")
            if original_clipboard is not None:
                pyperclip.copy(original_clipboard)
            return
            
        print(f"📖 [Typi Assistant] Captured text: \"{captured_text[:40]}...\"")
        print("🤖 [Typi Assistant] Sending payload to Gemini...")
        
        # Step 6: Process text via the AI Engine
        polished_text = ai_engine.process_text(captured_text)
        
        if polished_text == captured_text:
            print("✨ [Typi Assistant] Text is already optimal or could not be polished. Restoring clipboard.")
            pyperclip.copy(original_clipboard)
            return
            
        # Step 7: Put polished text on clipboard and paste it (Ctrl+V)
        pyperclip.copy(polished_text)
        print("✍️ [Typi Assistant] Replacing text with refined version...")
        keyboard.press_and_release('ctrl+v')
        time.sleep(CLIPBOARD_PASTE_DELAY)
        
        print("🎉 [Typi Assistant] Text successfully updated!")
        
    except Exception as e:
        print(f"❌ [Typi Assistant Error]: An unexpected error occurred: {str(e)}")
        
    finally:
        # Step 8: Always restore the user's original clipboard backup
        if original_clipboard is not None:
            try:
                pyperclip.copy(original_clipboard)
            except Exception as backup_err:
                print(f"⚠️ [Typi Assistant] Failed to restore original clipboard: {str(backup_err)}")

def main():
    print("=" * 60)
    print("🌀 Typi AI Writing Assistant Daemon (System-Wide)")
    print("=" * 60)
    print("Status: Active and running in the background.")
    print("Hotkey: Press [ Ctrl + Alt + A ] to polish any highlighted text.")
    print("Press [ Ctrl + C ] in this terminal window to exit.")
    print("-" * 60)
    
    # Register hotkey listener
    keyboard.add_hotkey('ctrl+alt+a', trigger_writing_assistant)
    
    # Block and wait for termination signal
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n👋 [Typi Assistant] Daemon shut down gracefully. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
