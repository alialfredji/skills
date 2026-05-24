---
name: yt-transcript
description: Fetch the transcript / subtitles of a YouTube video. Returns the full plain-text transcript that you can then summarize, analyze, or answer questions about.
allowed-tools: Bash(python3 *get-transcript.py*), Bash(brew install*), Bash(which yt-dlp*)
---

# YouTube Transcript Extraction

Extract plain-text transcripts from YouTube videos using yt-dlp.

## Prerequisites

yt-dlp must be installed. If missing, install it:

```bash
brew install yt-dlp
```

Verify with `which yt-dlp`. Python 3 is also required (ships with macOS).

## Usage

Run the bundled script from this skill's directory:

```bash
python3 <skill-dir>/scripts/get-transcript.py "<youtube-url>"
```

Options:
- `--lang <code>` — subtitle language (default: `en`). Examples: `es`, `fr`, `de`, `ja`

The script path is relative to this skill file. Use the absolute path:

```bash
python3 /Users/alialfredji/Obsidian/Laibyte/_claude-skills/yt-transcript/scripts/get-transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## What the Script Does

1. Extracts the video ID from the URL (supports youtube.com, youtu.be, shorts, embeds)
2. Calls yt-dlp to download subtitles in VTT format (tries manual subs first, falls back to auto-generated)
3. Parses VTT to plain text — strips timestamps, HTML tags, and deduplicates consecutive identical lines
4. Outputs clean transcript to stdout

## Error Handling

- **No yt-dlp**: Script exits with install instructions
- **No subtitles**: Reports that video has no subs in the requested language
- **Network errors**: Surfaces yt-dlp stderr for debugging

## When to Use

Use this skill whenever the user:
- Drops a YouTube URL and wants the transcript
- Asks to summarize, analyze, or extract content from a YouTube video
- Wants subtitles/captions from a video
- Needs to repurpose video content into text
