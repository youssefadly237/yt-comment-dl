"""Command-line interface for yt_comment_dl."""

import re
import argparse
import sys
import time
import json
from pathlib import Path

from .youtube_comment_downloader import YoutubeCommentDownloader
from .constants import SORT_BY_RECENT


def extract_video_id(url_or_id):
    """Extract video ID from YouTube URL or return as-is if already an ID."""
    if not url_or_id:
        return None

    # If it's already just an ID (11 characters, alphanumeric + _ -)
    if len(url_or_id) == 11 and url_or_id.replace("-", "").replace("_", "").isalnum():
        return url_or_id

    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/.*[?&]v=([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    return None


def comment_to_dict(comment):
    """Convert comment to dict if possible."""
    return comment.to_dict() if hasattr(comment, "to_dict") else comment


def format_comment(comment, pretty=False):
    """Format comment as JSON string."""
    if pretty:
        return json.dumps(comment, ensure_ascii=False, indent=2)
    return json.dumps(comment, ensure_ascii=False)


def write_comments(comment_dicts, output_path, pretty=False, limit=None):
    """Write comments to file as valid JSON array."""
    count = 0
    start_time = time.time()

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Collect all comments first to create valid JSON array
    comment_list = []
    for comment in comment_dicts:
        if limit and count >= limit:
            break
        comment_list.append(comment)
        count += 1
        print(f"\rDownloaded {count} comment(s)", end="", flush=True)

    # Write as valid JSON
    with open(output_path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(comment_list, f, ensure_ascii=False, indent=2)
        else:
            json.dump(comment_list, f, ensure_ascii=False)

    duration = time.time() - start_time
    print(f"\n[{duration:.2f} seconds] Downloaded {count} comments to {output_path}")
    return count


def main(argv=None):
    """CLI entry point for downloading YouTube comments."""
    parser = argparse.ArgumentParser(
        description="Download YouTube comments without using the YouTube API"
    )

    # URL/ID as positional argument
    parser.add_argument("url", help="YouTube video URL or video ID")

    # Output options
    parser.add_argument(
        "--output", "-o", help="Output filename (default: comments_<video_id>.json)"
    )
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print JSON output")

    # Download options
    parser.add_argument("--limit", "-l", type=int, help="Maximum number of comments to download")
    parser.add_argument("--language", "-a", help="Language for YouTube generated text (e.g. en)")
    parser.add_argument(
        "--sort",
        "-s",
        type=int,
        choices=[0, 1],
        default=SORT_BY_RECENT,
        help="Sort by: 0=popular, 1=recent (default: 1)",
    )

    try:
        args = parser.parse_args(argv)

        # Extract video ID from URL or use as-is
        video_id = extract_video_id(args.url)
        if not video_id:
            print(f"Error: Could not extract video ID from '{args.url}'")
            print("Please provide a valid YouTube URL or 11-character video ID")
            sys.exit(1)

        # Generate output filename if not provided
        output_file = args.output or f"comments_{video_id}.json"

        print(f"Downloading comments for video ID: {video_id}")
        print(f"Output file: {output_file}")

        downloader = YoutubeCommentDownloader()

        # Always use video ID (cleaner than URL parsing in downloader)
        comments = downloader.get_comments(video_id, args.sort, args.language)

        # Convert all comments to dicts up front
        def comment_dict_iterator():
            try:
                first_comment = next(comments)
            except StopIteration:
                print("No comments found.")
                return
            yield comment_to_dict(first_comment)
            for comment in comments:
                yield comment_to_dict(comment)

        # Write comments to file
        count = write_comments(comment_dict_iterator(), output_file, args.pretty, args.limit)

        if count == 0:
            print("No comments downloaded.")

    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
