import os
import tempfile
import time
from pathlib import Path
import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

# Typer sub-app for AI commands
app = typer.Typer(help="AI processing and analysis utilities.")
console = Console()

# Lazy imports for heavier libraries to optimize CLI startup time
def get_genai_client():
    """Initializes and returns the google-genai client."""
    # Ensure environment variables are loaded (main.py does this, but double check)
    if not os.environ.get("GEMINI_API_KEY"):
        console.print("[red]Error: GEMINI_API_KEY environment variable is not set.[/red]")
        console.print("[yellow]Please check that your .env file exists and contains GEMINI_API_KEY=your_key[/yellow]")
        raise typer.Exit(code=1)
        
    try:
        from google import genai
        return genai.Client()
    except ImportError:
        console.print("[red]Error: The 'google-genai' SDK is not installed or import failed.[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error initializing Gemini client: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command("analyze-video")
def analyze_video(
    video_path: str = typer.Argument(..., help="Path to the local video file to analyze.")
) -> None:
    """
    Extracts the audio data from a local video file, and uses the Gemini API
    to transcribe, analyze, and systematically organize the core arguments
    and philosophical claims found in the video.
    """
    path = Path(video_path).resolve()
    
    if not path.exists() or not path.is_file():
        console.print(f"[red]Error: Video file not found at '{video_path}'[/red]")
        raise typer.Exit(code=1)
        
    client = get_genai_client()
    
    # We will write the extracted audio to a temporary mp3 file
    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    audio_path = temp_audio_file.name
    temp_audio_file.close() # Close it so other programs can write to it
    
    try:
        # Step 1: Extract Audio
        with console.status("[bold cyan]Extracting audio from video file...[/bold cyan]", spinner="dots"):
            try:
                from moviepy.editor import VideoFileClip
            except ImportError:
                console.print("[red]Error: The 'moviepy' library is not installed. Run 'pip install moviepy' to extract audio.[/red]")
                raise typer.Exit(code=1)
                
            try:
                video = VideoFileClip(str(path))
                if video.audio is None:
                    raise ValueError("The provided video file does not contain any audio tracks.")
                video.audio.write_audiofile(audio_path, logger=None)
                video.close()
            except Exception as clip_err:
                console.print(f"[red]Audio extraction failed: {str(clip_err)}[/red]")
                raise typer.Exit(code=1)
                
        console.print("[green]Audio extraction complete.[/green]")
        
        # Step 2: Upload to Gemini Files API
        uploaded_file = None
        with console.status("[bold cyan]Uploading audio track to Gemini API...[/bold cyan]", spinner="dots"):
            try:
                uploaded_file = client.files.upload(file=audio_path)
            except Exception as upload_err:
                console.print(f"[red]Failed to upload audio to Gemini: {str(upload_err)}[/red]")
                raise typer.Exit(code=1)
                
        console.print(f"[green]Audio uploaded successfully. File Name: {uploaded_file.name}[/green]")
        
        # Step 3: Wait for file processing on Gemini (normally very fast for audio, but robust design requires it)
        with console.status("[bold cyan]Waiting for Gemini to process the audio file...[/bold cyan]", spinner="dots"):
            state = uploaded_file.state.name
            while state == "PROCESSING":
                time.sleep(2)
                uploaded_file = client.files.get(name=uploaded_file.name)
                state = uploaded_file.state.name
                
            if state == "FAILED":
                console.print("[red]Error: Gemini failed to process the audio file.[/red]")
                raise typer.Exit(code=1)
                
        console.print("[green]Gemini audio processing complete.[/green]")
        
        # Step 4: Generate structured analysis content
        analysis_prompt = (
            "You are an expert academic evaluator, philosophical analyst, and system logician. "
            "Your task is to transcribe (or summarize if transcription is trivial) the following audio file. "
            "Then, systematically organize the core arguments and philosophical claims found in it. "
            "Please structure your output using clean Markdown, following this format:\n\n"
            "# 🧠 Philosophical Argument & Claim Analysis\n\n"
            "## 📝 Overview & Context\n"
            "Provide a short paragraph summarizing the subject matter, the speaker's main thesis, and overall tone.\n\n"
            "## 🔑 Core Claims & Premises\n"
            "Represent the arguments systematically. Use a numbered list to state each core claim. "
            "If possible, format the primary argument as formal premises and a conclusion (e.g., Premise 1, Premise 2, Conclusion).\n\n"
            "## 🔍 Philosophical Themes & Concepts\n"
            "Detail the underlying philosophical schools of thought, frameworks, or key academic concepts referenced or implied.\n\n"
            "## ⚡ Logical Critique & Evaluation\n"
            "Evaluate the validity and soundness of the arguments. Highlight any logical fallacies, bias, rhetorical traps, or weak points.\n"
        )
        
        with console.status("[bold cyan]Generating deep reasoning analysis... (this may take a moment)[/bold cyan]", spinner="dots"):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[uploaded_file, analysis_prompt]
                )
            except Exception as gen_err:
                console.print(f"[red]Error generating analysis from model: {str(gen_err)}[/red]")
                raise typer.Exit(code=1)
                
        # Step 5: Render results using Rich Markdown
        console.print("\n[bold green]Analysis complete! Rending structured output:[/bold green]\n")
        console.print(Markdown(response.text))
        
        # Step 6: Remote file cleanup
        with console.status("[bold cyan]Cleaning up files on Gemini servers...[/bold cyan]", spinner="dots"):
            try:
                client.files.delete(name=uploaded_file.name)
                console.print("[green]Gemini storage cleaned up.[/green]")
            except Exception as cleanup_err:
                console.print(f"[yellow]Warning: Could not remove file from Gemini storage: {str(cleanup_err)}[/yellow]")
                
    except Exception as e:
        console.print(f"[red]Unexpected error in video analysis module: {str(e)}[/red]")
        raise typer.Exit(code=1)
    finally:
        # Step 7: Local temp file cleanup
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError as cleanup_err:
                console.print(f"[yellow]Warning: Could not remove local temp audio file: {str(cleanup_err)}[/yellow]")

@app.command("ask")
def ask_gemini(
    query: str = typer.Argument(..., help="The query/question to ask Gemini.")
) -> None:
    """
    Accepts a string query, sends it to Gemini, and streams the response
    back to the terminal using Rich markdown formatting.
    """
    client = get_genai_client()
    
    try:
        console.print(f"[cyan]Sending query to Gemini...[/cyan]\n")
        
        # Stream generation
        response = client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=query
        )
        
        accumulated_text = ""
        # Using Rich Live display to render markdown updates in real-time
        with Live(Markdown(""), refresh_per_second=10, auto_refresh=False) as live:
            for chunk in response:
                if chunk.text:
                    accumulated_text += chunk.text
                    live.update(Markdown(accumulated_text))
                    live.refresh()
                    
        console.print()  # Add an ending newline
        
    except Exception as e:
        console.print(f"[red]Error during generation stream: {str(e)}[/red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
