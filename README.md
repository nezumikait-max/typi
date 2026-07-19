# 🌀 Typi: AI Writing Assistant

`typi` is a lightweight, system-wide AI Writing Assistant for desktop. It runs quietly in the background as a daemon, listening for a global hotkey combination. When triggered, it grabs your highlighted text, refines it with Gemini's AI, and replaces it on the fly while preserving your clipboard history.

---

## 🚀 Features

- **System-Wide Operation**: Works in any editor, browser, terminal, or text field across your OS.
- **Instant Hotkey Activation**: Highlight any text and press `Ctrl + Alt + A` to refine it immediately.
- **Safety First (Clipboard Backup)**: Automatically backs up your current clipboard contents before capturing text and restores it immediately after pasting.
- **Collision Prevention**: Automatically releases the hotkey modifier keys before simulated keystrokes to ensure clean OS-level copy (`Ctrl+C`) and paste (`Ctrl+V`) triggers.
- **No Filler Output**: Utilizes a strict system prompt targeting `gemini-2.5-flash` to return only the corrected text without any conversational pleasantries or markdown wrappers.

---

## 🛠️ Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/nezumikait-max/typi.git
   cd typi
   ```

2. **Configure Environment variables**:
   Ensure you have a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Install Dependencies**:
   *Note: On Linux, `keyboard` may require running as root/sudo.*
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Assistant**:
   ```bash
   python assistant.py
   ```

---

## 📖 How to Use

1. Start `assistant.py`.
2. Highlight any text in any application (e.g. browser, Notepad, IDE, Slack).
3. Press **`Ctrl + Alt + A`**.
4. The console will report the status, and the highlighted text will be replaced in-place by the polished version.
5. Your original clipboard contents remain intact.
