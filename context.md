# 🌀 Typi Writing Assistant: Project Context

## 🎯 Project Overview
`typi` is a lightweight, system-wide AI Writing Assistant that runs as a background daemon. It mimics the seamless text correction features of Typi on Android, allowing users to rewrite and polish text inline using special triggers (`!fix`, `!email`, `!casual`, `!expand`) for activation and deactivation.

---

## 🛠️ Tech Stack & Architecture

### Core Technologies
- **Python 3.10+**: Core programming language.
- **keyboard**: Installs a global hook listening to keypresses to capture text. Disables listeners temporarily during simulation to avoid recursive typing. Simulates backspaces and typing to replace text on screen.
- **google-genai**: Google's official SDK interface to query the Gemini API.
- **python-dotenv**: Resolves environment configurations.

### Codebase Structure
The codebase consists of:
- [config.py](file:///C:/Users/eelri/.gemini/antigravity-cli/config.py): Resolves the `GEMINI_API_KEY` from env or local `.env`.
- [ai_engine.py](file:///C:/Users/eelri/.gemini/antigravity-cli/ai_engine.py): Communicates with `gemini-2.5-flash` using a strict system instruction to rewrite text according to the specific role prompt.
- [assistant.py](file:///C:/Users/eelri/.gemini/antigravity-cli/assistant.py): The main background daemon script running the inline trigger tracking, buffer compilation, backspace deletion, and replacement simulation.

---

## 🔒 Operational Flow & Safety Constraints
- **Self-Trigger Feedback Prevention**: Keyboard hooks are completely unregistered (`keyboard.unhook_all`) during simulated keystrokes to ensure simulated backspaces and replacement typing do not trigger recursive logging.
- **Cursor Safety**: Any explicit cursor movement (Arrow keys, Esc, Tab, Home, End) instantly resets the active trigger state to prevent deleting text from incorrect offsets if the user shifts the cursor position.
- **Backspace Calculations**: The daemon precisely counts characters to delete exactly:
  `[Length of Activation Trigger] + [Length of Captured Text] + [Length of Deactivation Trigger]`
  ensuring no unrelated surrounding text is altered.
- **Fallback Recovery**: If the API call fails or times out, the raw original text is written back to the screen so user inputs are never lost.
