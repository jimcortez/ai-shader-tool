"""Command-line interface for ISF Shader Renderer."""

import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import ShaderRendererConfig, load_config
from .renderer import ShaderRenderer

app = typer.Typer(
    name="isf-renderer",
    help="Render ISF shaders to PNG images at specified time codes",
    add_completion=False,
)
console = Console()


@app.command()
def main(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to YAML configuration file"
    ),
    shader: Optional[Path] = typer.Option(
        None, "--shader", "-s", help="Path to ISF shader file (or use stdin)"
    ),
    time: List[float] = typer.Option(
        [], "--time", "-t", help="Time code for rendering (can be specified multiple times)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    width: int = typer.Option(1920, "--width", "-w", help="Output width"),
    height: int = typer.Option(1080, "--height", "-h", help="Output height"),
    quality: int = typer.Option(95, "--quality", "-q", help="PNG quality (1-100)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Render ISF shaders to PNG images."""
    
    if verbose:
        console.print("[bold blue]ISF Shader Renderer[/bold blue]")
        console.print(f"Version: {__import__('isf_shader_renderer').__version__}")
    
    # Load configuration
    if isinstance(config_file, Path) and config_file:
        if not config_file.exists():
            console.print(f"[red]Error: Configuration file '{config_file}' not found[/red]")
            raise typer.Exit(1)
        
        try:
            cfg = load_config(config_file)
            if verbose:
                console.print(f"Loaded configuration from: {config_file}")
        except Exception as e:
            console.print(f"[red]Error loading configuration: {e}[/red]")
            raise typer.Exit(1)
    else:
        # Create default configuration
        cfg = ShaderRendererConfig()
        if verbose:
            console.print("Using default configuration")
    
    # Override configuration with command-line arguments
    if width != 1920 or height != 1080 or quality != 95:
        cfg.defaults.width = width
        cfg.defaults.height = height
        cfg.defaults.quality = quality
        if verbose:
            console.print("Applied command-line overrides")
    
    # Handle shader input
    if shader:
        if not shader.exists():
            console.print(f"[red]Error: Shader file '{shader}' not found[/red]")
            raise typer.Exit(1)
        shader_content = shader.read_text()
        if verbose:
            console.print(f"Loaded shader from: {shader}")
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            shader_content = sys.stdin.read()
            if verbose:
                console.print("Loaded shader from stdin")
        else:
            console.print("[red]Error: No shader file specified and no input from stdin[/red]")
            raise typer.Exit(1)
    
    # Validate time codes
    if not time and not cfg.shaders:
        console.print("[red]Error: No time codes specified[/red]")
        raise typer.Exit(1)
    
    # Create renderer
    renderer = ShaderRenderer(cfg)
    
    # Render shaders
    if config_file and cfg.shaders:
        # Use configuration file shaders
        render_from_config(renderer, cfg, verbose)
    else:
        # Use command-line arguments
        if not output:
            console.print("[red]Error: Output path required when not using config file[/red]")
            raise typer.Exit(1)
        
        render_single_shader(renderer, shader_content, time, output, verbose)


def render_from_config(renderer: ShaderRenderer, cfg: ShaderRendererConfig, verbose: bool) -> None:
    """Render shaders from configuration file."""
    total_shaders = len(cfg.shaders)
    total_frames = sum(len(shader.times) for shader in cfg.shaders)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"Rendering {total_shaders} shaders ({total_frames} frames total)...",
            total=total_frames,
        )
        
        for shader_config in cfg.shaders:
            if verbose:
                console.print(f"\nProcessing shader: {shader_config.input}")
            
            # Load shader content
            shader_path = Path(shader_config.input)
            if not shader_path.exists():
                console.print(f"[red]Warning: Shader file '{shader_path}' not found, skipping[/red]")
                continue
            
            shader_content = shader_path.read_text()
            
            # Render frames
            for i, time_code in enumerate(shader_config.times):
                output_path = Path(shader_config.output % i)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    renderer.render_frame(
                        shader_content, time_code, output_path, shader_config
                    )
                    progress.update(task, advance=1)
                    
                    if verbose:
                        console.print(f"  Rendered frame {i+1}/{len(shader_config.times)} at time {time_code}s")
                        
                except Exception as e:
                    console.print(f"[red]Error rendering frame {i+1} at time {time_code}s: {e}[/red]")
    
    console.print(f"\n[green]Successfully rendered {total_frames} frames from {total_shaders} shaders[/green]")


def render_single_shader(
    renderer: ShaderRenderer,
    shader_content: str,
    time_codes: List[float],
    output_path: Path,
    verbose: bool,
) -> None:
    """Render a single shader with multiple time codes."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"Rendering {len(time_codes)} frames...",
            total=len(time_codes),
        )
        
        for i, time_code in enumerate(time_codes):
            # Handle output path formatting
            if "%" in str(output_path):
                frame_path = Path(str(output_path) % i)
            else:
                frame_path = output_path
            
            try:
                renderer.render_frame(shader_content, time_code, frame_path)
                progress.update(task, advance=1)
                
                if verbose:
                    console.print(f"Rendered frame {i+1}/{len(time_codes)} at time {time_code}s")
                    
            except Exception as e:
                console.print(f"[red]Error rendering frame {i+1} at time {time_code}s: {e}[/red]")
    
    console.print(f"\n[green]Successfully rendered {len(time_codes)} frames[/green]")


@app.command()
def info() -> None:
    """Show information about the ISF Shader Renderer."""
    table = Table(title="ISF Shader Renderer Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Version", __import__('isf_shader_renderer').__version__)
    table.add_row("Author", __import__('isf_shader_renderer').__author__)
    table.add_row("Description", "Render ISF shaders to PNG images at specified time codes")
    
    console.print(table)


if __name__ == "__main__":
    app() 