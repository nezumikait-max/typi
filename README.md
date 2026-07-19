# 🌀 Antigravity CLI

`antigravity` is a modular, production-ready CLI utility belt that bundles local filesystem automation and advanced Gemini-driven analytical processors under a single clean toolchain.

## 🚀 Features

### 📂 Files Module
- **`shuffle`**: Recursively shuffles the locations of all files in a folder, cleans up defunct directories, and produces an interactive, search-enabled HTML directory layout tree (`antigravity_map.html`).
- **`clean`**: Groups and sorts all root files in a folder into categorized directories (`images`, `documents`, `audio`, `videos`, `archives`, `code`, `executables`, `other`) based on their extensions.

### 🧠 AI Module
- **`analyze-video`**: Extracts audio from local video files, uploads the track to Gemini using the Files API, transcribes the claims, and produces a structured critical and logical analysis of the video's arguments.
- **`ask`**: Sends text questions to Gemini, rendering the response with real-time streaming markdown directly in the terminal interface.

---

## 🛠️ Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/nezumikait-max/antigravity.git
   cd antigravity
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Install Dependencies**:
   It is recommended to run this inside a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

## 📖 Command Reference

### File Shuffling
```bash
python main.py files shuffle "C:/path/to/target/folder"
```
*Rearranges the file system configuration and writes `antigravity_map.html` in the target directory.*

### File Organizing (Cleaning)
```bash
python main.py files clean "C:/path/to/target/folder"
```
*Sorts root files into categorized extension folders.*

### Ask Gemini (Text Streaming)
```bash
python main.py ai ask "Explain the logical structure of a reductio ad absurdum argument."
```
*Streams Gemini's markdown response directly to the console.*

### Video Analysis (Logical & Argument Critique)
```bash
python main.py ai analyze-video "C:/path/to/philosophical_lecture.mp4"
```
*Transcribes and parses underlying premises, fallacies, and structural validity.*
