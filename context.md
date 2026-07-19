# 🌀 Antigravity Project Context

## 🎯 Project Overview
`antigravity` is a modular, high-performance CLI utility belt designed for developers and systems engineers. It integrates local file system automation utilities with advanced AI capabilities powered by the Google Gemini API.

---

## 🛠️ Tech Stack & Architecture

### Core Technologies
- **Python 3.10+**: Core programming language.
- **Typer**: CLI routing and argument/option parsing.
- **Rich**: Terminal output styling, streaming Markdown rendering, and loading state visuals.
- **python-dotenv**: Environment configuration resolution.
- **google-genai**: Official Google GenAI SDK interface.
- **moviepy**: Audio track extraction from video files.

### Sub-Module Architecture
The application uses a modular directory namespace layout:
- [main.py](file:///C:/Users/eelri/.gemini/antigravity-cli/main.py): Registers command routers and loads environment tokens.
- [commands/files.py](file:///C:/Users/eelri/.gemini/antigravity-cli/commands/files.py): Handles local I/O operations (shuffling structures and extensions organization).
- [commands/ai.py](file:///C:/Users/eelri/.gemini/antigravity-cli/commands/ai.py): Handles integration with the Gemini API (multimodal audio analysis and query streams).

---

## 🔒 Security & Safe-Handling Constraints
- **Ignore files**: All credentials, local logs, caches, and runtime databases are strictly excluded via `.gitignore` to prevent leaking private client tokens.
- **No Tracebacks**: All database, network, API, and filesystem interactions are wrapped in graceful exception blocks. Rather than emitting Python tracebacks, the app prints error messages formatted via Rich's standard console.
- **Remote Data Cleanup**: Temporary audio assets are deleted immediately from both local disks and the remote Gemini Files storage API.

---

## 🎨 Visual Map Features
The `shuffle` command generates a premium, dark-mode visual map ([antigravity_map.html](file:///C:/Users/eelri/.gemini/antigravity-cli/antigravity_map.html)) of the randomized structure. The interface features:
- Glassmorphic card overlays.
- A responsive collapsable folder tree (`<details>` / `<summary>`).
- Interactive Javascript filtering to search for files.
- Gradient typography matching developer dashboards.
