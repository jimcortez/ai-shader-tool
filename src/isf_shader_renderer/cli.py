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
from .utils import format_error_for_ai, format_success_for_ai

app = typer.Typer(
    name="isf-shader-render",
    help="Render ISF shaders to PNG images at specified time codes",
    add_completion=False,
)
console = Console()


# Only register the main function as the Typer command/callback
@app.command('isf-render')
def isf_render(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to YAML configuration file"
    ),
    shader: Path = typer.Argument(
        ..., help="Path to ISF shader file (use '-' for stdin)"
    ),
    time: List[float] = typer.Option(
        [],
        "--time",
        "-t",
        help="Time code for rendering (can be specified multiple times)",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    width: int = typer.Option(1920, "--width", "-w", help="Output width"),
    height: int = typer.Option(1080, "--height", "-h", help="Output height"),
    quality: int = typer.Option(95, "--quality", "-q", help="PNG quality (1-100)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
<<<<<<< HEAD
=======

    info: bool = typer.Option(
        False,
        "--info",
        help="Show information about the renderer and shader before rendering",
    ),
    ai_info: bool = typer.Option(
        False,
        "--ai-info",
        help="Format output for AI processing (natural language, no colors/emojis)",
    ),
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
    inputs: Optional[str] = typer.Option(
        None,
        "--inputs",
        help="Shader input values as comma-separated key=value pairs (e.g. foo=1,bar=2.0,baz=hello)",
    ),
) -> None:
    """Render ISF shaders to PNG images."""

<<<<<<< HEAD
    if verbose:
=======
    # Validate that --info and --ai-info are not used together
    if info and ai_info:
        console.print("[red]Error: --info and --ai-info flags cannot be used together[/red]")
        raise typer.Exit(1)

    if verbose and not ai_info:
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
        console.print("[bold blue]ISF Shader Renderer[/bold blue]")
        console.print(f"Version: {__import__('isf_shader_renderer').__version__}")

    # Load configuration
    if isinstance(config_file, Path) and config_file:
        if not config_file.exists():
            if ai_info:
                print(f"Error: Configuration file '{config_file}' not found")
            else:
                console.print(
                    f"[red]Error: Configuration file '{config_file}' not found[/red]"
                )
            raise typer.Exit(1)
<<<<<<< HEAD
=======

>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
        try:
            cfg = load_config(config_file)
            if verbose and not ai_info:
                console.print(f"Loaded configuration from: {config_file}")
        except Exception as e:
            if ai_info:
                print(format_error_for_ai(e, "configuration loading"))
            else:
                console.print(f"[red]Error loading configuration: {e}[/red]")
            raise typer.Exit(1)
    else:
        # Create default configuration
        cfg = ShaderRendererConfig()
        if verbose and not ai_info:
            console.print("Using default configuration")

    # Override configuration with command-line arguments
    if width != 1920 or height != 1080 or quality != 95:
        cfg.defaults.width = width
        cfg.defaults.height = height
        cfg.defaults.quality = quality
        if verbose and not ai_info:
            console.print("Applied command-line overrides")

    # Handle shader input
    if str(shader) == "-":
        # Read from stdin
        if not sys.stdin.isatty():
            shader_content = sys.stdin.read()
            if verbose and not ai_info:
                console.print("Loaded shader from stdin")
        else:
<<<<<<< HEAD
            console.print("[red]Error: No input from stdin[/red]")
            raise typer.Exit(1)
    else:
        if not shader.exists():
            console.print(f"[red]Error: Shader file '{shader}' not found[/red]")
            raise typer.Exit(1)
        shader_content = shader.read_text()
        if verbose:
=======
            if ai_info:
                print("Error: No input from stdin")
            else:
                console.print(
                    "[red]Error: No input from stdin[/red]"
                )
            raise typer.Exit(1)
    else:
        if not shader.exists():
            if ai_info:
                print(f"Error: Shader file '{shader}' not found")
            else:
                console.print(f"[red]Error: Shader file '{shader}' not found[/red]")
            raise typer.Exit(1)
        shader_content = shader.read_text()
        if verbose and not ai_info:
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
            console.print(f"Loaded shader from: {shader}")

    # Create renderer (will crash if VVISF is not available)
    try:
        renderer = ShaderRenderer(cfg)
    except ImportError as e:
<<<<<<< HEAD
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Show info if requested
    if False: # info: # Removed info command
=======
        if ai_info:
            print(format_error_for_ai(e, "renderer initialization"))
        else:
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Show info if requested
    if info and not ai_info:
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
        # Renderer info
        table = Table(title="ISF Shader Renderer Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Version", __import__("isf_shader_renderer").__version__)
        table.add_row("Author", getattr(__import__("isf_shader_renderer"), "__author__", ""))
        table.add_row(
            "Description", "Render ISF shaders to PNG images at specified time codes"
        )
        console.print(table)
        # Shader info
        shader_info = renderer.get_shader_info(shader_content)
        shader_table = Table(title="Shader Information")
        for k, v in shader_info.items():
            if k == "inputs":
                shader_table.add_row("inputs", str([i["name"] for i in v]))
            else:
                shader_table.add_row(str(k), str(v))
        console.print(shader_table)

    # Parse inputs string into a dictionary
    input_dict = {}
    if inputs:
        for pair in inputs.split(","):
            if not pair.strip():
                continue
            if "=" not in pair:
<<<<<<< HEAD
                console.print(
                    f"[red]Invalid input format: {pair} (expected key=value)[/red]"
                )
=======
                if ai_info:
                    print(f"Invalid input format: {pair} (expected key=value)")
                else:
                    console.print(
                        f"[red]Invalid input format: {pair} (expected key=value)[/red]"
                    )
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
                raise typer.Exit(1)
            key, value = pair.split("=", 1)
            input_dict[key.strip()] = value.strip()

    # Render shaders
    if config_file and cfg.shaders:
        # Use configuration file shaders
        render_from_config(renderer, cfg, verbose, ai_info)
    else:
        # Use command-line arguments
        if not output:
<<<<<<< HEAD
            console.print(
                "[red]Error: Output path required when not using config file[/red]"
            )
=======
            if ai_info:
                print("Error: Output path required when not using config file")
            else:
                console.print(
                    "[red]Error: Output path required when not using config file[/red]"
                )
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
            raise typer.Exit(1)
        # If inputs are provided, create a ShaderConfig and pass to renderer
        shader_config = None
        if input_dict:
            from .config import ShaderConfig

            shader_config = ShaderConfig(
                input=str(shader) if str(shader) != "-" else "<stdin>",
                output=str(output),
                times=time or [0.0],
                width=width,
                height=height,
                quality=quality,
                inputs=input_dict,
            )
        # Default to time 0.0 if no time codes are specified
        time_codes = time if time else [0.0]
        try:
            render_single_shader(
                renderer,
                shader_content,
                time_codes,
                output,
                verbose,
                shader_config,
<<<<<<< HEAD
            )
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
=======
                ai_info,
            )
        except Exception as e:
            if ai_info:
                print(format_error_for_ai(e, "shader rendering"))
            else:
                console.print(f"[red]Error: {e}[/red]")
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
            raise typer.Exit(1)


def render_from_config(
    renderer: ShaderRenderer,
<<<<<<< HEAD
    cfg: Config,
    verbose: bool,
=======
    cfg: ShaderRendererConfig,
    verbose: bool,
    ai_info: bool = False,
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
) -> None:
    """Render shaders from configuration file."""
    total_shaders = len(cfg.shaders)
    total_frames = sum(len(shader.times) for shader in cfg.shaders)

<<<<<<< HEAD
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
                console.print(
                    f"[red]Warning: Shader file '{shader_path}' not found, skipping[/red]"
                )
=======
    if not ai_info:
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
                    console.print(
                        f"[red]Warning: Shader file '{shader_path}' not found, skipping[/red]"
                    )
                    continue

                shader_content = shader_path.read_text()

                # Render frames
                for i, time_code in enumerate(shader_config.times):
                    output_path = Path(shader_config.output % i)
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    try:
                        renderer.render_frame(
                            shader_content,
                            time_code,
                            output_path,
                            shader_config,
                        )
                        progress.update(task, advance=1)

                        if verbose:
                            console.print(
                                f"  Rendered frame {i+1}/{len(shader_config.times)} at time {time_code}s"
                            )

                    except Exception as e:
                        console.print(
                            f"[red]Error rendering frame {i+1} at time {time_code}s: {e}[/red]"
                        )

        console.print(
            f"\n[green]Successfully rendered {total_frames} frames from {total_shaders} shaders[/green]"
        )
    else:
        # AI-friendly output mode
        successful_frames = 0
        failed_frames = 0

        for shader_config in cfg.shaders:
            # Load shader content
            shader_path = Path(shader_config.input)
            if not shader_path.exists():
                print(f"Warning: Shader file '{shader_path}' not found, skipping")
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
                continue

            shader_content = shader_path.read_text()

            # Render frames
            for i, time_code in enumerate(shader_config.times):
                output_path = Path(shader_config.output % i)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    renderer.render_frame(
                        shader_content,
                        time_code,
                        output_path,
                        shader_config,
                    )
<<<<<<< HEAD
                    progress.update(task, advance=1)

                    if verbose:
                        console.print(
                            f"  Rendered frame {i+1}/{len(shader_config.times)} at time {time_code}s"
                        )

                except Exception as e:
                    console.print(
                        f"[red]Error rendering frame {i+1} at time {time_code}s: {e}[/red]"
                    )

    console.print(
        f"\n[green]Successfully rendered {total_frames} frames from {total_shaders} shaders[/green]"
    )
=======
                    successful_frames += 1

                except Exception as e:
                    failed_frames += 1
                    print(format_error_for_ai(e, f"rendering frame {i+1} at time {time_code}s"))

        if failed_frames == 0:
            print(format_success_for_ai(successful_frames))
        else:
            print(f"Completed rendering with {successful_frames} successful frames and {failed_frames} failed frames from {total_shaders} shaders")
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54


def render_single_shader(
    renderer: ShaderRenderer,
    shader_content: str,
    time_codes: List[float],
    output_path: Path,
    verbose: bool,
    shader_config=None,
<<<<<<< HEAD
=======
    ai_info: bool = False,
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54
) -> None:
    """Render a single shader with multiple time codes."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

<<<<<<< HEAD
    successful_frames = 0
    failed_frames = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"Rendering {len(time_codes)} frames...",
            total=len(time_codes),
        )
=======
    if not ai_info:
        successful_frames = 0
        failed_frames = 0
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
                    renderer.render_frame(
                        shader_content,
                        time_code,
                        frame_path,
                        shader_config,
                    )
                    progress.update(task, advance=1)
                    successful_frames += 1

                    if verbose:
                        console.print(
                            f"Rendered frame {i+1}/{len(time_codes)} at time {time_code}s"
                        )

                except Exception as e:
                    failed_frames += 1
                    console.print(
                        f"[red]Error rendering frame {i+1} at time {time_code}s: {e}[/red]"
                    )

        if failed_frames == 0:
            console.print(f"\n[green]Successfully rendered {successful_frames} frames[/green]")
        else:
            console.print(f"\n[yellow]Completed rendering with {successful_frames} successful frame(s) and {failed_frames} failed frame(s)[/yellow]")
    else:
        # AI-friendly output mode
        successful_frames = 0
        failed_frames = 0
>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54

        for i, time_code in enumerate(time_codes):
            # Handle output path formatting
            if "%" in str(output_path):
                frame_path = Path(str(output_path) % i)
            else:
                frame_path = output_path

            try:
                renderer.render_frame(
                    shader_content,
                    time_code,
                    frame_path,
                    shader_config,
                )
<<<<<<< HEAD
                progress.update(task, advance=1)
                successful_frames += 1

                if verbose:
                    console.print(
                        f"Rendered frame {i+1}/{len(time_codes)} at time {time_code}s"
                    )

            except Exception as e:
                failed_frames += 1
                console.print(
                    f"[red]Error rendering frame {i+1} at time {time_code}s: {e}[/red]"
                )

    if failed_frames == 0:
        console.print(f"\n[green]Successfully rendered {successful_frames} frames[/green]")
    else:
        console.print(f"\n[yellow]Completed rendering with {successful_frames} successful frame(s) and {failed_frames} failed frame(s)[/yellow]")


# Move info and mcp_server to standalone functions (not Typer commands)
# def info_command(): # Removed info command
#     """Show information about the ISF Shader Renderer."""
#     table = Table(title="ISF Shader Renderer Information")
#     table.add_column("Property", style="cyan")
#     table.add_column("Value", style="magenta")
#     table.add_row("Version", __import__('isf_shader_renderer').__version__)
#     table.add_row("Author", __import__('isf_shader_renderer').__author__)
#     table.add_row("Description", "Render ISF shaders to PNG images at specified time codes")
#     console.print(table)
=======
                successful_frames += 1

            except Exception as e:
                failed_frames += 1
                print(format_error_for_ai(e, f"rendering frame {i+1} at time {time_code}s"))

        if failed_frames == 0:
            print(format_success_for_ai(successful_frames))
        else:
            print(f"Completed rendering with {successful_frames} successful frames and {failed_frames} failed frames")


def cli():
    """Entry point for the CLI."""
    app()

>>>>>>> 43e6b06c995869d9d0ab4c0203d0367da54c3d54

if __name__ == "__main__":
    cli()
