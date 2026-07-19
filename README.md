# 🌀 Typi: AI Writing Assistant

`typi` is a lightweight, system-wide AI Writing Assistant for desktop. It runs quietly in the background as a daemon, listening to your keystrokes globally. When it detects an inline trigger, it enters recording mode. When you type the same trigger again, it automatically deletes your input, refines it with Gemini's AI, and types the polished text back to the screen.

---

## 🚀 Features

- **Inline Triggers**: No complex keyboard combinations or highlighting required. Just type a trigger to start, write your text, and type the trigger again to replace it!
- **System-Wide Operation**: Works in any editor, browser, chat window, terminal, or input field.
- **Self-Trigger Protection**: Automatically suspends keyboard capturing during replacement simulation to prevent recursive loops.
- **Accurate Deletion**: Deletes exactly the characters you typed plus the activation and deactivation tags.
- **Safety Fallback**: Restores original text if the API request fails.

---

## 📖 Trigger Options

- **`!fix`**: Grammatical corrections and typo repairs.
- **`!email`**: Rewriting text into a professional, polished business email.
- **`!casual`**: Converting formal drafts into warm, friendly conversational text.
- **`!expand`**: Expanding quick bullet points or notes into full, rich paragraphs.

---

## 🛠️ Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/nezumikait-max/typi.git
   cd typi
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Install Dependencies**:
   *Note: On Linux, `keyboard` may require root privileges.*
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Assistant**:
   ```bash
   python assistant.py
   ```

---

## 💡 Usage Example

1. Open any text box (e.g. Notepad, Slack, a web form).
2. Type the activation trigger: **`!fix`**
3. Type your raw message with mistakes: **`this is normaly how i write but with typo`**
4. Type the deactivation trigger: **`!fix`**
5. Typi will instantly delete the whole line back to the start of `!fix`, process it, and type out:
   **`This is normally how I write, but with a typo.`**
