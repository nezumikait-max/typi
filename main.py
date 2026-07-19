import sys
from pathlib import Path
import typer
from dotenv import load_dotenv

# Load environment variables from the .env file at the absolute root of execution
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import sub-modules
from commands import files, ai

# Initialize main Typer app
app = typer.Typer(
    name="typi",
    help="🌀 Typi: A modular CLI utility belt for modern systems engineers.",
    add_completion=True
)

# Add sub-command groups
app.add_typer(files.app, name="files")
app.add_typer(ai.app, name="ai")

@app.callback()
def main_callback():
    """
    Typi CLI - Shuffles structures, cleans directories, and processes multimodal inputs.
    """
    pass

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        from rich.console import Console
        Console().print(f"[red]Fatal startup error: {str(e)}[/red]")
        sys.exit(1)
