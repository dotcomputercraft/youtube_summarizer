# YouTube Video Summarizer - Usage Guide

This guide provides comprehensive examples and use cases for the YouTube Video Summarizer CLI tool.

## Quick Start

1. **Set up your API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **Basic usage:**
   ```bash
   ./yt-summarizer summarize https://youtube.com/watch?v=VIDEO_ID
   ```

## Command Reference

### Global Options

Available for all commands:

- `--verbose, -v`: Enable detailed output
- `--quiet, -q`: Show only errors
- `--config-file, -c PATH`: Use custom config file
- `--api-key TEXT`: Override API key
- `--model TEXT`: Use different OpenAI model (default: gpt-4o)

### Commands Overview

| Command | Purpose | Example |
|---------|---------|---------|
| `summarize` | Generate AI summary | `yt-summarizer summarize VIDEO_ID` |
| `extract` | Get raw transcript | `yt-summarizer extract VIDEO_ID` |
| `batch` | Process multiple videos | `yt-summarizer batch urls.txt` |
| `info` | Show transcript info | `yt-summarizer info VIDEO_ID` |
| `config-info` | Show configuration | `yt-summarizer config-info` |

## Detailed Command Usage

### 1. Summarize Command

Generate intelligent summaries of YouTube videos.

#### Basic Syntax
```bash
yt-summarizer summarize [OPTIONS] URL_OR_VIDEO_ID
```

#### Options
- `--style, -s`: Summary style (brief, detailed, bullet_points, key_insights, academic, casual)
- `--max-length, -l`: Maximum words in summary
- `--output, -o`: Save to file
- `--format, -f`: Output format (text, json, markdown)
- `--language, -lang`: Preferred transcript languages
- `--save-transcript`: Save raw transcript to file
- `--custom-prompt`: Use custom summarization prompt

#### Examples

**Basic summarization:**
```bash
./yt-summarizer summarize "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

**Brief summary with file output:**
```bash
./yt-summarizer summarize dQw4w9WgXcQ --style brief --output summary.txt
```

**JSON format with metadata:**
```bash
./yt-summarizer summarize VIDEO_ID --format json --output data.json
```

**Markdown with custom length:**
```bash
./yt-summarizer summarize VIDEO_ID \
  --format markdown \
  --max-length 200 \
  --output report.md
```

**Multi-language with transcript save:**
```bash
./yt-summarizer summarize VIDEO_ID \
  --language es --language en \
  --save-transcript transcript.txt \
  --style detailed
```

**Custom prompt:**
```bash
./yt-summarizer summarize VIDEO_ID \
  --custom-prompt "Summarize focusing on technical concepts and code examples"
```

### 2. Extract Command

Extract raw transcripts without summarization.

#### Basic Syntax
```bash
yt-summarizer extract [OPTIONS] URL_OR_VIDEO_ID
```

#### Options
- `--output, -o`: Save to file
- `--format, -f`: Output format (text, json, srt)
- `--language, -lang`: Preferred languages
- `--timestamps`: Include timestamps

#### Examples

**Basic extraction:**
```bash
./yt-summarizer extract "https://youtube.com/watch?v=VIDEO_ID"
```

**With timestamps:**
```bash
./yt-summarizer extract VIDEO_ID --timestamps
```

**SRT subtitle format:**
```bash
./yt-summarizer extract VIDEO_ID --format srt --output subtitles.srt
```

**JSON with metadata:**
```bash
./yt-summarizer extract VIDEO_ID --format json --output transcript.json
```

**Specific language:**
```bash
./yt-summarizer extract VIDEO_ID --language es --output spanish_transcript.txt
```

### 3. Batch Command

Process multiple videos from a file.

#### Basic Syntax
```bash
yt-summarizer batch [OPTIONS] INPUT_FILE
```

#### Options
- `--style, -s`: Summary style for all videos
- `--output-dir, -d`: Directory for output files
- `--format, -f`: Output format
- `--max-length, -l`: Maximum summary length
- `--concurrent, -j`: Number of concurrent requests (default: 3)

#### Input File Format

Create a text file with one URL or video ID per line:

```
https://youtube.com/watch?v=VIDEO1
https://youtu.be/VIDEO2
VIDEO3
https://youtube.com/watch?v=VIDEO4&t=30s
```

#### Examples

**Basic batch processing:**
```bash
./yt-summarizer batch video_list.txt
```

**Save to directory:**
```bash
./yt-summarizer batch urls.txt --output-dir summaries/
```

**Custom style and format:**
```bash
./yt-summarizer batch urls.txt \
  --style key_insights \
  --format markdown \
  --output-dir reports/
```

**High concurrency:**
```bash
./yt-summarizer batch large_list.txt --concurrent 10
```

**Brief summaries with length limit:**
```bash
./yt-summarizer batch urls.txt \
  --style brief \
  --max-length 50 \
  --format json
```

### 4. Info Command

Get information about available transcripts.

#### Basic Syntax
```bash
yt-summarizer info URL_OR_VIDEO_ID
```

#### Example
```bash
./yt-summarizer info dQw4w9WgXcQ
```

**Output:**
```
ℹ Getting transcript information for video: dQw4w9WgXcQ
✓ Found 2 available transcript(s):
  • English (en) - 👤 Manual | 🌐 Translatable
  • Spanish (es) - 🤖 Auto-generated
```

### 5. Config-info Command

Show current configuration and test API connection.

#### Basic Syntax
```bash
yt-summarizer config-info
```

#### Example Output
```
ℹ Current Configuration:
  Model: gpt-4o
  API Key: Set
  Verbose: False
  Quiet: False

ℹ Model Information:
  Model: gpt-4o
  Api Base: https://api.openai.com/v1
  Api Key Set: True
```

## Summary Styles Explained

### Brief
- 2-3 sentences
- Main topic and key takeaway
- Perfect for quick overviews

**Example:**
```bash
./yt-summarizer summarize VIDEO_ID --style brief
```

### Detailed
- Comprehensive summary
- Multiple paragraphs
- Includes main topics, key points, and conclusions
- Default style

**Example:**
```bash
./yt-summarizer summarize VIDEO_ID --style detailed
```

### Bullet Points
- Organized list format
- Easy to scan
- Main topic followed by key points

**Example:**
```bash
./yt-summarizer summarize VIDEO_ID --style bullet_points
```

### Key Insights
- Focus on learnings and takeaways
- Important facts and data
- Actionable advice
- Notable quotes

**Example:**
```bash
./yt-summarizer summarize VIDEO_ID --style key_insights
```

### Academic
- Formal scholarly language
- Abstract/overview structure
- Main arguments with supporting evidence
- Conclusions section

**Example:**
```bash
./yt-summarizer summarize VIDEO_ID --style academic
```

### Casual
- Conversational tone
- Easy to understand
- As if explaining to a friend

**Example:**
```bash
./yt-summarizer summarize VIDEO_ID --style casual
```

## Output Formats

### Text (Default)
Plain text output, perfect for reading or further processing.

```bash
./yt-summarizer summarize VIDEO_ID --format text
```

### JSON
Structured data with metadata, ideal for programmatic use.

```json
{
  "video_id": "dQw4w9WgXcQ",
  "style": "detailed",
  "summary": "This video explains...",
  "transcript_length": 1250,
  "summary_length": 180
}
```

```bash
./yt-summarizer summarize VIDEO_ID --format json
```

### Markdown
Formatted text with headers, perfect for documentation.

```markdown
# Video Summary

**Video ID:** dQw4w9WgXcQ
**Style:** detailed

## Summary

This video explains...
```

```bash
./yt-summarizer summarize VIDEO_ID --format markdown
```

### SRT (Extract only)
Subtitle format with timestamps.

```
1
00:00:00,000 --> 00:00:02,500
Welcome to this tutorial

2
00:00:02,500 --> 00:00:05,500
Today we will learn about Python
```

```bash
./yt-summarizer extract VIDEO_ID --format srt
```

## Advanced Use Cases

### 1. Research Workflow

Process educational videos for research:

```bash
# Create list of educational videos
echo "https://youtube.com/watch?v=EDUCATIONAL1" > research_videos.txt
echo "https://youtube.com/watch?v=EDUCATIONAL2" >> research_videos.txt

# Generate academic summaries
./yt-summarizer batch research_videos.txt \
  --style academic \
  --format markdown \
  --output-dir research_summaries/

# Extract full transcripts for detailed analysis
./yt-summarizer batch research_videos.txt \
  --format json \
  --output-dir transcripts/ \
  --concurrent 5
```

### 2. Content Creation Pipeline

Summarize competitor videos:

```bash
# Quick competitive analysis
./yt-summarizer summarize COMPETITOR_VIDEO \
  --style key_insights \
  --custom-prompt "Focus on unique selling points and strategies mentioned"
```

### 3. Learning and Note-taking

Create study materials from lectures:

```bash
# Detailed notes
./yt-summarizer summarize LECTURE_VIDEO \
  --style detailed \
  --format markdown \
  --output lecture_notes.md \
  --save-transcript full_transcript.txt

# Quick review points
./yt-summarizer summarize LECTURE_VIDEO \
  --style bullet_points \
  --max-length 300
```

### 4. Accessibility

Create subtitles and summaries:

```bash
# Generate SRT subtitles
./yt-summarizer extract VIDEO_ID \
  --format srt \
  --output subtitles.srt

# Create accessible summary
./yt-summarizer summarize VIDEO_ID \
  --style casual \
  --format text \
  --output accessible_summary.txt
```

### 5. Multi-language Processing

Handle international content:

```bash
# Try Spanish first, fallback to English
./yt-summarizer summarize VIDEO_ID \
  --language es --language en \
  --style detailed

# Extract transcript in original language
./yt-summarizer extract VIDEO_ID \
  --language es \
  --timestamps \
  --output spanish_transcript.txt
```

## Error Handling and Troubleshooting

### Common Error Messages

1. **"Could not extract video ID"**
   - Check URL format
   - Ensure video is public
   - Try using just the video ID

2. **"Failed to extract transcript"**
   - Video may not have captions
   - Try different language options
   - Check if video is age-restricted

3. **"OpenAI API key is required"**
   - Set environment variable: `export OPENAI_API_KEY="your-key"`
   - Or use `--api-key` flag

4. **"Rate limit exceeded"**
   - Reduce `--concurrent` value
   - Wait before retrying
   - Check your OpenAI usage limits

### Debug Mode

Enable verbose output for troubleshooting:

```bash
./yt-summarizer --verbose summarize VIDEO_ID
```

This will show:
- Detailed processing steps
- API request information
- Error stack traces
- Timing information

### Quiet Mode

For automated scripts, suppress all output except errors:

```bash
./yt-summarizer --quiet batch urls.txt --output-dir results/
```

## Performance Tips

1. **Batch Processing**: Use batch command for multiple videos
2. **Concurrency**: Adjust `--concurrent` based on your API limits
3. **Caching**: Save transcripts separately to avoid re-extraction
4. **Length Limits**: Use `--max-length` to control summary size
5. **Format Choice**: Use JSON for programmatic processing

## Integration Examples

### Shell Scripts

```bash
#!/bin/bash
# Process all videos in a playlist

PLAYLIST_URLS="playlist_urls.txt"
OUTPUT_DIR="summaries"

mkdir -p "$OUTPUT_DIR"

./yt-summarizer batch "$PLAYLIST_URLS" \
  --style detailed \
  --format markdown \
  --output-dir "$OUTPUT_DIR" \
  --concurrent 3

echo "Processing complete. Summaries saved to $OUTPUT_DIR/"
```

### Python Integration

```python
import subprocess
import json

def summarize_video(video_id, style="detailed"):
    """Summarize a video and return JSON result."""
    cmd = [
        "./yt-summarizer", "summarize", video_id,
        "--style", style,
        "--format", "json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise Exception(f"Error: {result.stderr}")

# Usage
summary_data = summarize_video("dQw4w9WgXcQ", "brief")
print(summary_data["summary"])
```

This comprehensive usage guide should help users get the most out of the YouTube Video Summarizer tool!

