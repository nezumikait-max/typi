# 🌀 Typi Writing Assistant: Project Context

## 🎯 Project Overview
`typi` is a lightweight, system-wide AI Writing Assistant that runs as a background daemon. It mimics the seamless text correction features of Typi on Android, allowing users to polish any highlighted text globally across the operating system.

---

## 🛠️ Tech Stack & Architecture

### Core Technologies
- **Python 3.10+**: Core programming language.
- **keyboard**: Intercepts the global hotkey (`Ctrl+Alt+A`), monitors event hooks, and programmatically simulates keystrokes (`Ctrl+C` and `Ctrl+V`).
- **pyperclip**: Reads from and writes to the system clipboard.
- **google-genai**: Google's official SDK interface to query the Gemini API.
- **python-dotenv**: Resolves environment configurations.

### Codebase Structure
The codebase consists of:
- [config.py](file:///C:/Users/eelri/.gemini/antigravity-cli/config.py): Resolves the `GEMINI_API_KEY` from env or local `.env`.
- [ai_engine.py](file:///C:/Users/eelri/.gemini/antigravity-cli/ai_engine.py): Communicates with `gemini-2.5-flash` using a strict system instruction to rewrite text without meta-dialogue.
- [assistant.py](file:///C:/Users/eelri/.gemini/antigravity-cli/assistant.py): The main background daemon script running clipboard backups, hotkey interception, and key simulations.

---

## 🔒 Security & Race-Condition Constraints
- **Key Modifier Collisions**: Hotkey modifier keys (`ctrl`, `alt`, `a`) are explicitly released prior to copying or pasting to avoid interferences like `ctrl+alt+c` registering with the OS.
- **No Data Loss**: The user's clipboard contents are immediately backed up before replacement, cleared to detect highlighting success, and restored immediately after paste execution.
- **Graceful Error Handling**: OS-level keystrokes, clipboard interactions, and API payloads are wrapped in try-except-finally blocks to keep the daemon running continuously.
