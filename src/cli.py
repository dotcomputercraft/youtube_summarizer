"""
Command Line Interface for YouTube Video Summarizer

This module provides a comprehensive CLI interface similar to Cobra from Go,
with multiple commands, subcommands, and extensive configuration options.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
from colorama import init, Fore, Style
from dotenv import load_dotenv
from tqdm import tqdm

try:
    from .transcript_extractor import TranscriptExtractor
    from .summarizer import Summarizer, SummaryStyle
except ImportError:
    from transcript_extractor import TranscriptExtractor
    from summarizer import Summarizer, SummaryStyle


# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Load environment variables
load_dotenv()


class Config:
    """Configuration management for the CLI."""
    
    def __init__(self):
        self.verbose = False
        self.quiet = False
        self.output_format = 'text'
        self.config_file = None
        self.api_key = None
        self.model = 'gpt-4o'
        
    def setup_logging(self):
        """Setup logging based on verbosity settings."""
        if self.quiet:
            level = logging.ERROR
        elif self.verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO
            
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


# Global configuration object
config = Config()


def print_success(message: str):
    """Print success message in green."""
    click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message in red."""
    click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", err=True)


def print_warning(message: str):
    """Print warning message in yellow."""
    click.echo(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message in blue."""
    click.echo(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def save_output(content: str, output_file: Optional[str] = None, format_type: str = 'text'):
    """Save output to file or print to stdout."""
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if format_type == 'json':
                    json.dump(json.loads(content) if isinstance(content, str) else content, f, indent=2)
                else:
                    f.write(content)
            print_success(f"Output saved to {output_file}")
        except Exception as e:
            print_error(f"Failed to save output: {e}")
    else:
        click.echo(content)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output except errors')
@click.option('--config-file', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
@click.option('--model', default='gpt-4o', help='OpenAI model to use')
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx, verbose, quiet, config_file, api_key, model):
    """
    YouTube Video Summarizer - Extract and summarize YouTube video transcripts using GPT-4o.
    
    This tool provides powerful commands to extract transcripts from YouTube videos
    and generate intelligent summaries using OpenAI's GPT-4o model.
    
    Examples:
        yt-summarizer summarize https://youtube.com/watch?v=VIDEO_ID
        yt-summarizer extract VIDEO_ID --output transcript.txt
        yt-summarizer batch urls.txt --style brief
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Update global config
    config.verbose = verbose
    config.quiet = quiet
    config.config_file = config_file
    config.api_key = api_key
    config.model = model
    config.setup_logging()
    
    # Store config in context
    ctx.obj['config'] = config


@cli.command()
@click.argument('url_or_video_id')
@click.option('--style', '-s', 
              type=click.Choice(['brief', 'detailed', 'bullet_points', 'key_insights', 'academic', 'casual']),
              default='detailed', 
              help='Summary style')
@click.option('--max-length', '-l', type=int, help='Maximum summary length in words')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['text', 'json', 'markdown']),
              default='text',
              help='Output format')
@click.option('--language', '-lang', multiple=True, help='Preferred transcript languages (e.g., en, es)')
@click.option('--save-transcript', type=click.Path(), help='Save raw transcript to file')
@click.option('--custom-prompt', help='Custom summarization prompt')
@click.pass_context
def summarize(ctx, url_or_video_id, style, max_length, output, output_format, language, save_transcript, custom_prompt):
    """
    Summarize a YouTube video from URL or video ID.
    
    This command extracts the transcript from a YouTube video and generates
    an intelligent summary using GPT-4o.
    
    Examples:
        yt-summarizer summarize https://youtube.com/watch?v=dQw4w9WgXcQ
        yt-summarizer summarize dQw4w9WgXcQ --style brief
        yt-summarizer summarize VIDEO_ID --output summary.txt --format markdown
    """
    try:
        # Initialize components
        extractor = TranscriptExtractor()
        summarizer = Summarizer(api_key=config.api_key, model=config.model)
        
        # Extract video ID
        video_id = extractor.extract_video_id(url_or_video_id)
        if not video_id:
            print_error(f"Could not extract video ID from: {url_or_video_id}")
            sys.exit(1)
        
        print_info(f"Processing video: {video_id}")
        
        # Extract transcript
        with tqdm(total=3, desc="Processing") as pbar:
            pbar.set_description("Extracting transcript")
            
            language_codes = list(language) if language else None
            transcript = extractor.extract_transcript(video_id, language_codes)
            
            if not transcript:
                print_error("Failed to extract transcript")
                print_warning("This could be because:")
                print_warning("  • The video doesn't have captions/transcripts enabled")
                print_warning("  • The video is private, age-restricted, or unavailable")
                print_warning("  • There's a temporary issue with YouTube's transcript service")
                print_info("Try using a different video or check if the video has captions enabled")
                sys.exit(1)
            
            pbar.update(1)
            
            # Save transcript if requested
            if save_transcript:
                with open(save_transcript, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                print_success(f"Transcript saved to {save_transcript}")
            
            pbar.set_description("Generating summary")
            pbar.update(1)
            
            # Generate summary
            summary_style = SummaryStyle(style)
            summary = summarizer.summarize(
                transcript, 
                style=summary_style, 
                max_length=max_length,
                custom_prompt=custom_prompt
            )
            
            if not summary:
                print_error("Failed to generate summary")
                sys.exit(1)
            
            pbar.update(1)
            pbar.set_description("Complete")
        
        # Format output
        if output_format == 'json':
            result = {
                'video_id': video_id,
                'style': style,
                'summary': summary,
                'transcript_length': len(transcript.split()),
                'summary_length': len(summary.split())
            }
            output_content = json.dumps(result, indent=2)
        elif output_format == 'markdown':
            output_content = f"# Video Summary\n\n**Video ID:** {video_id}\n**Style:** {style}\n\n## Summary\n\n{summary}"
        else:
            output_content = summary
        
        # Save or print output
        save_output(output_content, output, output_format)
        
        if not output and not config.quiet:
            print_success("Summary generated successfully!")
        
    except Exception as e:
        print_error(f"Error: {e}")
        if config.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('url_or_video_id')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['text', 'json', 'srt']),
              default='text',
              help='Output format')
@click.option('--language', '-lang', multiple=True, help='Preferred transcript languages')
@click.option('--timestamps', is_flag=True, help='Include timestamps in output')
@click.pass_context
def extract(ctx, url_or_video_id, output, output_format, language, timestamps):
    """
    Extract transcript from a YouTube video.
    
    This command extracts the raw transcript without summarization.
    
    Examples:
        yt-summarizer extract https://youtube.com/watch?v=VIDEO_ID
        yt-summarizer extract VIDEO_ID --format json --timestamps
        yt-summarizer extract VIDEO_ID --output transcript.txt
    """
    try:
        extractor = TranscriptExtractor()
        
        # Extract video ID
        video_id = extractor.extract_video_id(url_or_video_id)
        if not video_id:
            print_error(f"Could not extract video ID from: {url_or_video_id}")
            sys.exit(1)
        
        print_info(f"Extracting transcript for video: {video_id}")
        
        language_codes = list(language) if language else None
        
        if timestamps or output_format in ['json', 'srt']:
            # Get transcript with timestamps
            transcript_data = extractor.get_transcript_with_timestamps(video_id, language_codes)
            if not transcript_data:
                print_error("Failed to extract transcript")
                sys.exit(1)
            
            if output_format == 'json':
                output_content = json.dumps(transcript_data, indent=2)
            elif output_format == 'srt':
                # Convert to SRT format
                srt_content = []
                for i, segment in enumerate(transcript_data, 1):
                    start_time = segment['start']
                    duration = segment['duration']
                    end_time = start_time + duration
                    
                    start_srt = f"{int(start_time//3600):02d}:{int((start_time%3600)//60):02d}:{start_time%60:06.3f}".replace('.', ',')
                    end_srt = f"{int(end_time//3600):02d}:{int((end_time%3600)//60):02d}:{end_time%60:06.3f}".replace('.', ',')
                    
                    srt_content.append(f"{i}\n{start_srt} --> {end_srt}\n{segment['text']}\n")
                
                output_content = '\n'.join(srt_content)
            else:
                # Text format with timestamps
                output_content = '\n'.join([f"[{seg['start']:.2f}s] {seg['text']}" for seg in transcript_data])
        else:
            # Get plain text transcript
            transcript = extractor.extract_transcript(video_id, language_codes)
            if not transcript:
                print_error("Failed to extract transcript")
                sys.exit(1)
            
            output_content = transcript
        
        save_output(output_content, output, output_format)
        
        if not output and not config.quiet:
            print_success("Transcript extracted successfully!")
        
    except Exception as e:
        print_error(f"Error: {e}")
        if config.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--style', '-s', 
              type=click.Choice(['brief', 'detailed', 'bullet_points', 'key_insights', 'academic', 'casual']),
              default='detailed', 
              help='Summary style')
@click.option('--output-dir', '-d', type=click.Path(), help='Output directory for summaries')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['text', 'json', 'markdown']),
              default='text',
              help='Output format')
@click.option('--max-length', '-l', type=int, help='Maximum summary length in words')
@click.option('--concurrent', '-j', type=int, default=3, help='Number of concurrent requests')
@click.pass_context
def batch(ctx, input_file, style, output_dir, output_format, max_length, concurrent):
    """
    Process multiple YouTube videos from a file.
    
    Input file should contain one YouTube URL or video ID per line.
    
    Examples:
        yt-summarizer batch urls.txt --style brief
        yt-summarizer batch video_ids.txt --output-dir summaries/
        yt-summarizer batch urls.txt --format json --concurrent 5
    """
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print_error("No URLs found in input file")
            sys.exit(1)
        
        print_info(f"Processing {len(urls)} videos")
        
        # Create output directory if specified
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        extractor = TranscriptExtractor()
        summarizer = Summarizer(api_key=config.api_key, model=config.model)
        
        results = []
        failed = []
        
        with tqdm(total=len(urls), desc="Processing videos") as pbar:
            for i, url in enumerate(urls):
                try:
                    # Extract video ID
                    video_id = extractor.extract_video_id(url)
                    if not video_id:
                        failed.append(f"Invalid URL: {url}")
                        pbar.update(1)
                        continue
                    
                    pbar.set_description(f"Processing {video_id}")
                    
                    # Extract transcript
                    transcript = extractor.extract_transcript(video_id)
                    if not transcript:
                        failed.append(f"Failed to extract transcript: {video_id}")
                        pbar.update(1)
                        continue
                    
                    # Generate summary
                    summary_style = SummaryStyle(style)
                    summary = summarizer.summarize(transcript, style=summary_style, max_length=max_length)
                    
                    if not summary:
                        failed.append(f"Failed to generate summary: {video_id}")
                        pbar.update(1)
                        continue
                    
                    # Store result
                    result = {
                        'video_id': video_id,
                        'url': url,
                        'summary': summary,
                        'style': style
                    }
                    results.append(result)
                    
                    # Save individual file if output directory specified
                    if output_dir:
                        filename = f"{video_id}.{output_format}"
                        filepath = Path(output_dir) / filename
                        
                        if output_format == 'json':
                            with open(filepath, 'w', encoding='utf-8') as f:
                                json.dump(result, f, indent=2)
                        elif output_format == 'markdown':
                            content = f"# Video Summary\n\n**Video ID:** {video_id}\n**URL:** {url}\n**Style:** {style}\n\n## Summary\n\n{summary}"
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(content)
                        else:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(summary)
                    
                    pbar.update(1)
                    
                except Exception as e:
                    failed.append(f"Error processing {url}: {e}")
                    pbar.update(1)
                    continue
        
        # Print results
        print_success(f"Successfully processed {len(results)} videos")
        
        if failed:
            print_warning(f"Failed to process {len(failed)} videos:")
            for failure in failed:
                print_error(f"  {failure}")
        
        # Save batch results if no output directory
        if not output_dir and results:
            batch_output = f"batch_results.{output_format}"
            if output_format == 'json':
                with open(batch_output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
            else:
                with open(batch_output, 'w', encoding='utf-8') as f:
                    for result in results:
                        f.write(f"=== {result['video_id']} ===\n")
                        f.write(f"URL: {result['url']}\n")
                        f.write(f"Style: {result['style']}\n\n")
                        f.write(result['summary'])
                        f.write("\n\n" + "="*50 + "\n\n")
            
            print_success(f"Batch results saved to {batch_output}")
        
    except Exception as e:
        print_error(f"Error: {e}")
        if config.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('url_or_video_id')
@click.pass_context
def info(ctx, url_or_video_id):
    """
    Get information about a YouTube video's available transcripts.
    
    Examples:
        yt-summarizer info https://youtube.com/watch?v=VIDEO_ID
        yt-summarizer info VIDEO_ID
    """
    try:
        extractor = TranscriptExtractor()
        
        # Extract video ID
        video_id = extractor.extract_video_id(url_or_video_id)
        if not video_id:
            print_error(f"Could not extract video ID from: {url_or_video_id}")
            sys.exit(1)
        
        print_info(f"Getting transcript information for video: {video_id}")
        
        # Get available transcripts
        transcripts = extractor.get_available_transcripts(video_id)
        
        if not transcripts:
            print_warning("No transcripts available for this video")
            sys.exit(0)
        
        print_success(f"Found {len(transcripts)} available transcript(s):")
        
        for transcript in transcripts:
            status_icons = []
            if transcript['is_generated']:
                status_icons.append("🤖 Auto-generated")
            else:
                status_icons.append("👤 Manual")
            
            if transcript['is_translatable']:
                status_icons.append("🌐 Translatable")
            
            status = " | ".join(status_icons)
            
            click.echo(f"  • {transcript['language']} ({transcript['language_code']}) - {status}")
        
    except Exception as e:
        print_error(f"Error: {e}")
        if config.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.pass_context
def config_info(ctx):
    """Show current configuration and model information."""
    try:
        print_info("Current Configuration:")
        click.echo(f"  Model: {config.model}")
        click.echo(f"  API Key: {'Set' if config.api_key else 'Not set'}")
        click.echo(f"  Verbose: {config.verbose}")
        click.echo(f"  Quiet: {config.quiet}")
        
        if config.api_key:
            try:
                summarizer = Summarizer(api_key=config.api_key, model=config.model)
                model_info = summarizer.get_model_info()
                
                print_info("Model Information:")
                for key, value in model_info.items():
                    click.echo(f"  {key.replace('_', ' ').title()}: {value}")
                
            except Exception as e:
                print_warning(f"Could not connect to API: {e}")
        else:
            print_warning("Set OPENAI_API_KEY environment variable to test API connection")
        
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()

