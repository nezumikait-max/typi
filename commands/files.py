import os
import random
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="File automation utilities.")
console = Console()

# HTML template for directory visualization
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Typi Directory Map</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --panel-bg: rgba(30, 41, 59, 0.7);
            --border-color: rgba(99, 102, 241, 0.2);
            --glow-color: rgba(99, 102, 241, 0.3);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #6366f1;
            --accent-hover: #818cf8;
            --folder-color: #f59e0b;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .container {
            width: 100%;
            max-width: 900px;
            background: var(--panel-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 2.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 40px var(--glow-color);
            margin-top: 1rem;
        }
        
        header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(to right, #a5b4fc, #818cf8, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        header p {
            color: var(--text-muted);
            font-size: 1.1rem;
        }
        
        .search-box {
            position: relative;
            margin-bottom: 2rem;
            width: 100%;
        }
        
        .search-box input {
            width: 100%;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .search-box input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
        }
        
        .tree-view {
            padding: 1.5rem;
            background: rgba(15, 23, 42, 0.4);
            border-radius: 8px;
            max-height: 600px;
            overflow-y: auto;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        details.folder {
            margin: 0.5rem 0;
            border-left: 1px dashed rgba(99, 102, 241, 0.3);
            padding-left: 1.2rem;
            transition: all 0.2s ease;
        }
        
        details.folder:first-of-type {
            border-left: none;
            padding-left: 0;
        }
        
        summary.folder-summary {
            list-style: none;
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 0.6rem;
            border-radius: 6px;
            transition: background 0.2s;
            user-select: none;
        }
        
        summary.folder-summary:hover {
            background: rgba(99, 102, 241, 0.1);
        }
        
        summary.folder-summary::-webkit-details-marker {
            display: none;
        }
        
        .icon {
            margin-right: 0.75rem;
            font-size: 1.3rem;
        }
        
        .name {
            font-weight: 500;
        }
        
        .badge {
            font-size: 0.8rem;
            background: rgba(99, 102, 241, 0.2);
            color: var(--accent-hover);
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            margin-left: 0.75rem;
            font-weight: 400;
        }
        
        .folder-content {
            margin-top: 0.25rem;
        }
        
        .file {
            display: flex;
            align-items: center;
            padding: 0.5rem 0.6rem;
            margin: 0.25rem 0 0.25rem 1.2rem;
            border-radius: 6px;
            transition: all 0.2s;
        }
        
        .file:hover {
            background: rgba(255, 255, 255, 0.05);
            transform: translateX(4px);
        }
        
        .file .size {
            margin-left: auto;
            font-size: 0.85rem;
            color: var(--text-muted);
        }
        
        .highlight {
            background: rgba(234, 179, 8, 0.2) !important;
            border: 1px solid rgba(234, 179, 8, 0.5);
            border-radius: 4px;
        }
        
        footer {
            margin-top: auto;
            padding: 2rem 0;
            color: var(--text-muted);
            font-size: 0.9rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌀 Typi Directory Map</h1>
            <p>Interactive Visualization of Shuffled Directory Structure</p>
        </header>
        
        <div class="search-box">
            <input type="text" id="search" placeholder="Search files by name...">
        </div>
        
        <div class="tree-view">
            __TREE_CONTENT__
        </div>
    </div>
    
    <footer>
        Generated with 🌀 Typi CLI | __GENERATED_TIME__
    </footer>

    <script>
        const searchInput = document.getElementById('search');
        
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const files = document.querySelectorAll('.file');
            
            files.forEach(file => {
                const name = file.getAttribute('data-name').toLowerCase();
                if (query && name.includes(query)) {
                    file.classList.add('highlight');
                    let parent = file.parentElement;
                    while (parent) {
                        if (parent.tagName === 'DETAILS') {
                            parent.open = true;
                        }
                        parent = parent.parentElement;
                    }
                } else {
                    file.classList.remove('highlight');
                }
            });
        });
    </script>
</body>
</html>
"""

def build_tree(path: Path) -> Dict[str, Any]:
    """Recursively builds a tree dictionary of directories and files."""
    tree = {"name": path.name or str(path), "type": "directory", "children": []}
    try:
        for entry in path.iterdir():
            if entry.name.startswith('.') or entry.name == "typi_map.html":
                continue
            if entry.is_dir():
                tree["children"].append(build_tree(entry))
            else:
                size = entry.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} B"
                tree["children"].append({
                    "name": entry.name,
                    "type": "file",
                    "size": size_str,
                    "ext": entry.suffix.lower()
                })
    except Exception as e:
        console.print(f"[yellow]Warning: Could not read path {entry}: {str(e)}[/yellow]")
        
    # Sort: Directories first, then files
    tree["children"].sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
    return tree

def render_tree_to_html(node: Dict[str, Any]) -> str:
    """Renders the tree dictionary to recursive HTML string."""
    if node["type"] == "directory":
        html = f"""
        <details open class="folder">
            <summary class="folder-summary">
                <span class="icon">📁</span>
                <span class="name">{node['name']}</span>
                <span class="badge">{len(node['children'])} items</span>
            </summary>
            <div class="folder-content">
        """
        for child in node["children"]:
            html += render_tree_to_html(child)
        html += """
            </div>
        </details>
        """
        return html
    else:
        # Resolve file icons based on extension
        icon = "📄"
        ext = node.get("ext", "")
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']:
            icon = "🖼️"
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
            icon = "🎵"
        elif ext in ['.mp4', '.mkv', '.avi', '.mov', '.wmv']:
            icon = "🎥"
        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.md']:
            icon = "📝"
        elif ext in ['.zip', '.tar', '.gz', '.rar', '.7z']:
            icon = "📦"
        elif ext in ['.py', '.js', '.ts', '.html', '.css', '.json', '.c', '.cpp', '.rs', '.go']:
            icon = "💻"
            
        return f"""
        <div class="file" data-name="{node['name']}">
            <span class="icon">{icon}</span>
            <span class="name">{node['name']}</span>
            <span class="size">{node['size']}</span>
        </div>
        """

def generate_html_map(target_path: Path) -> None:
    """Generates the HTML map file inside target_path."""
    try:
        console.print("[cyan]Generating HTML map layout...[/cyan]")
        tree = build_tree(target_path)
        tree_html = ""
        for child in tree["children"]:
            tree_html += render_tree_to_html(child)
            
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content = HTML_TEMPLATE.replace("__TREE_CONTENT__", tree_html)
        html_content = html_content.replace("__GENERATED_TIME__", now_str)
        
        output_file = target_path / "typi_map.html"
        output_file.write_text(html_content, encoding="utf-8")
        
        # Output visual link
        uri = output_file.resolve().as_uri()
        console.print(f"[green]HTML map generated: [/green][bold underline cyan]{uri}[/bold underline cyan]")
    except Exception as e:
        console.print(f"[red]Error generating HTML map: {str(e)}[/red]")

def cleanup_empty_dirs(directory: Path) -> None:
    """Removes empty directories recursively under directory."""
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
            except OSError:
                pass

@app.command("shuffle")
def shuffle_directory(
    target_dir: str = typer.Argument(..., help="The target directory path to shuffle.")
) -> None:
    """
    Recursively scans a target directory path, systematically shuffles the folder contents,
    and dynamically generates an HTML map layout displaying the new directory structure.
    """
    target_path = Path(target_dir).resolve()
    
    if not target_path.exists() or not target_path.is_dir():
        console.print(f"[red]Error: The path '{target_dir}' does not exist or is not a directory.[/red]")
        raise typer.Exit(code=1)
        
    try:
        # Find all files recursively, excluding the generated HTML map itself and hidden files
        files: List[Path] = [
            p for p in target_path.rglob('*') 
            if p.is_file() and p.name != "typi_map.html" and not p.name.startswith('.')
        ]
        
        if len(files) < 2:
            console.print("[yellow]Warning: At least 2 files are required in the target directory to shuffle.[/yellow]")
            # Even if we can't shuffle, let's still generate a map of the current structure
            generate_html_map(target_path)
            return
            
        console.print(f"[cyan]Scanning target directory... Found {len(files)} files.[/cyan]")
        
        # Save relative paths of all files
        relative_paths = [p.relative_to(target_path) for p in files]
        
        # Create a shuffled mapping of destinations
        shuffled_relative_paths = list(relative_paths)
        random.shuffle(shuffled_relative_paths)
        
        # Use a temporary directory to handle moving and avoid overwriting files in transition
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            console.print("[cyan]Caching files to temporary workspace...[/cyan]")
            
            # Step 1: Copy files to temp location
            temp_files = []
            for idx, file_path in enumerate(files):
                temp_file = temp_path / f"shuf_{idx}_{file_path.name}"
                shutil.copy2(file_path, temp_file)
                temp_files.append((temp_file, shuffled_relative_paths[idx]))
                
            # Step 2: Delete original files
            console.print("[cyan]Clearing original files...[/cyan]")
            for file_path in files:
                try:
                    file_path.unlink()
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not remove file {file_path}: {e}[/yellow]")
            
            # Clean up empty folders so we don't end up with dead directories
            cleanup_empty_dirs(target_path)
            
            # Step 3: Write files to their shuffled relative destinations
            console.print("[cyan]Writing files in shuffled configuration...[/cyan]")
            for temp_file, dest_rel_path in temp_files:
                dest_file_path = target_path / dest_rel_path
                dest_file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(temp_file), str(dest_file_path))
                
        console.print("[green]Systematic shuffle complete.[/green]")
        
        # Generate the map HTML visualization
        generate_html_map(target_path)
        
    except Exception as e:
        console.print(f"[red]Error during shuffle: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command("clean")
def clean_directory(
    target_dir: str = typer.Argument(..., help="The target directory path to clean and organize.")
) -> None:
    """
    Organizes a target directory by moving files into sub-folders based on their file extensions.
    """
    target_path = Path(target_dir).resolve()
    
    if not target_path.exists() or not target_path.is_dir():
        console.print(f"[red]Error: The path '{target_dir}' does not exist or is not a directory.[/red]")
        raise typer.Exit(code=1)
        
    # Standard extension categories
    extension_map = {
        # Images
        '.png': 'images', '.jpg': 'images', '.jpeg': 'images', '.gif': 'images', 
        '.bmp': 'images', '.svg': 'images', '.webp': 'images', '.ico': 'images',
        # Documents
        '.pdf': 'documents', '.doc': 'documents', '.docx': 'documents', 
        '.xls': 'documents', '.xlsx': 'documents', '.ppt': 'documents', 
        '.pptx': 'documents', '.txt': 'documents', '.csv': 'documents', 
        '.md': 'documents', '.rtf': 'documents',
        # Audio
        '.mp3': 'audio', '.wav': 'audio', '.ogg': 'audio', '.flac': 'audio', 
        '.m4a': 'audio', '.aac': 'audio',
        # Videos
        '.mp4': 'videos', '.mkv': 'videos', '.avi': 'videos', '.mov': 'videos', 
        '.wmv': 'videos', '.flv': 'videos',
        # Archives
        '.zip': 'archives', '.tar': 'archives', '.gz': 'archives', '.rar': 'archives', 
        '.7z': 'archives', '.bz2': 'archives',
        # Code/Dev
        '.py': 'code', '.js': 'code', '.ts': 'code', '.html': 'code', 
        '.css': 'code', '.json': 'code', '.c': 'code', '.cpp': 'code', 
        '.h': 'code', '.rs': 'code', '.go': 'code', '.sh': 'code', '.bat': 'code',
        # Executables
        '.exe': 'executables', '.msi': 'executables', '.apk': 'executables', '.dmg': 'executables'
    }
    
    try:
        # Collect files in the ROOT of the target directory to avoid recursive confusion
        files_to_move: List[Path] = [
            p for p in target_path.iterdir() 
            if p.is_file() and p.name != "typi_map.html" and not p.name.startswith('.')
        ]
        
        if not files_to_move:
            console.print("[yellow]No files found in the root directory to clean.[/yellow]")
            return
            
        console.print(f"[cyan]Cleaning root directory... Found {len(files_to_move)} files.[/cyan]")
        
        # Move count trackers
        moves: Dict[str, List[str]] = {}
        
        for file_path in files_to_move:
            suffix = file_path.suffix.lower()
            folder_name = extension_map.get(suffix, 'other')
            
            dest_dir = target_path / folder_name
            dest_dir.mkdir(exist_ok=True)
            
            dest_path = dest_dir / file_path.name
            
            # Handle potential name collisions
            counter = 1
            original_stem = file_path.stem
            while dest_path.exists():
                dest_path = dest_dir / f"{original_stem}_{counter}{suffix}"
                counter += 1
                
            shutil.move(str(file_path), str(dest_path))
            
            if folder_name not in moves:
                moves[folder_name] = []
            moves[folder_name].append(file_path.name)
            
        # Display summary in a beautiful Rich Table
        table = Table(title="Clean Directory Summary", show_header=True, header_style="bold magenta")
        table.add_column("Category Folder", style="cyan")
        table.add_column("Files Moved", style="green")
        table.add_column("Count", style="bold yellow")
        
        total_moved = 0
        for folder, file_names in sorted(moves.items()):
            file_list_str = ", ".join(file_names[:5])
            if len(file_names) > 5:
                file_list_str += f" (+{len(file_names) - 5} more)"
            table.add_row(folder, file_list_str, str(len(file_names)))
            total_moved += len(file_names)
            
        console.print(table)
        console.print(f"[green]Successfully cleaned and sorted {total_moved} files.[/green]")
        
    except Exception as e:
        console.print(f"[red]Error during clean operation: {str(e)}[/red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
