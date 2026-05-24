#!/usr/bin/env python3
"""
YouTube Transcript Extractor
Uses yt-dlp to download subtitles and converts VTT to plain text.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile


def extract_video_id(url: str) -> str:
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")


def vtt_to_plain_text(vtt_content: str) -> str:
    """Convert VTT subtitle content to plain text.
    
    Strips timestamps, HTML tags, and deduplicates consecutive identical lines.
    Ported from alialfredji/yt-transcript-mcp vttToPlainText().
    """
    lines = vtt_content.split('\n')
    text_lines = []
    prev_line = None

    for line in lines:
        # Skip VTT header
        if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            continue
        # Skip timestamp lines
        if re.match(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->', line):
            continue
        # Skip numeric cue identifiers
        if re.match(r'^\d+$', line.strip()):
            continue
        # Strip HTML tags
        cleaned = re.sub(r'<[^>]+>', '', line).strip()
        if not cleaned:
            continue
        # Deduplicate consecutive identical lines
        if cleaned != prev_line:
            text_lines.append(cleaned)
            prev_line = cleaned

    return '\n'.join(text_lines)


def fetch_transcript(url: str, lang: str = 'en') -> str:
    video_id = extract_video_id(url)
    
    if not shutil.which('yt-dlp'):
        print("ERROR: yt-dlp not found. Install with: brew install yt-dlp", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, video_id)
        
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--write-subs',
            '--write-auto-subs',
            '--sub-lang', lang,
            '--sub-format', 'vtt',
            '--output', output_template,
            url,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed:\n{result.stderr}")

        # VTT files can be named .{lang}.vtt or .{lang}.auto.vtt
        vtt_file = None
        for f in os.listdir(tmpdir):
            if f.endswith('.vtt'):
                vtt_file = os.path.join(tmpdir, f)
                break

        if not vtt_file:
            raise RuntimeError(
                f"No subtitle file found. Video may not have subtitles in '{lang}'.\n"
                f"yt-dlp stdout: {result.stdout}\n"
                f"yt-dlp stderr: {result.stderr}"
            )

        with open(vtt_file, 'r', encoding='utf-8') as f:
            vtt_content = f.read()

        return vtt_to_plain_text(vtt_content)


def main():
    parser = argparse.ArgumentParser(description='Fetch YouTube transcript')
    parser.add_argument('url', help='YouTube video URL or video ID')
    parser.add_argument('--lang', default='en', help='Subtitle language code (default: en)')
    args = parser.parse_args()

    try:
        transcript = fetch_transcript(args.url, args.lang)
        print(transcript)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()