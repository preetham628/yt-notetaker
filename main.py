import os
from typing import List

import typer

from yt_notetaker.notetaker import generate_playlist_docx, generate_single_video_docx


app = typer.Typer(help="Generate DOCX files of YouTube playlist transcripts.")


@app.command()
def generate(
    playlist_urls: List[str] = typer.Argument(..., help="One or more YouTube playlist URLs."),
    output_dir: str = typer.Option("playlists_docx", "--output-dir", "-o", help="Directory to save DOCX files."),
    use_llm: bool = typer.Option(True, "--use-llm/--no-llm", help="Enable LLM summarization and outline."),
    model: str = typer.Option("gpt-4o-mini", "--model", help="LLM model for summarization."),
    include_raw_transcript: bool = typer.Option(False, "--include-raw/--no-include-raw", help="Include raw transcript in DOCX (not recommended)."),
    max_workers: int = typer.Option(250, "--max-workers", help="Max parallel threads for LLM calls."),
):
    """Generate DOCX files for provided playlist URLs."""
    os.makedirs(output_dir, exist_ok=True)
    for url in playlist_urls:
        typer.echo(f"Processing playlist: {url}")
        generate_playlist_docx(
            url,
            output_dir=output_dir,
            use_llm=use_llm,
            llm_model=model,
            include_raw_transcript=include_raw_transcript,
            max_workers=max_workers,
        )


@app.command()
def generate_single(
    video_url: str = typer.Argument(..., help="A single YouTube video URL."),
    output_dir: str = typer.Option("playlists_docx", "--output-dir", "-o", help="Directory to save DOCX files."),
    use_llm: bool = typer.Option(True, "--use-llm/--no-llm", help="Enable LLM summarization and outline."),
    model: str = typer.Option("gpt-4o-mini", "--model", help="LLM model for summarization."),
):
    os.makedirs(output_dir, exist_ok=True)
    typer.echo(f"Processing video: {video_url}")
    path = generate_single_video_docx(
        video_url,
        output_dir=output_dir,
        use_llm=use_llm,
        llm_model=model,
    )
    typer.echo(f"Saved: {path}")


def main():
    app()


if __name__ == "__main__":
    main()
