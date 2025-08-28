# yt-comment-dl

Simple script for downloading YouTube comments without using the YouTube API. The output is in JSON format.

**This is a maintained fork of [egbertbouman/youtube-comment-downloader](https://github.com/egbertbouman/youtube-comment-downloader).**

## Installation

Preferably inside a [python virtual environment](https://virtualenv.pypa.io/en/latest/) install this package via:

```bash
pip install yt-comment-dl
```

Or directly from the GitHub repository:

```bash
pip install git+https://github.com/youssefadly237/yt-comment-dl.git
```

## Usage as command-line interface

```bash
$ yt-comment-dl --help
usage: yt-comment-dl [-h] [--output OUTPUT] [--pretty] [--limit LIMIT] [--language LANGUAGE] [--sort {0,1}] url

Download YouTube comments without using the YouTube API

positional arguments:
  url                                    YouTube video URL or video ID

options:
  -h, --help                             Show this help message and exit
  --output OUTPUT, -o OUTPUT             Output filename (default: comments_<video_id>.json)
  --pretty, -p                           Pretty-print JSON output
  --limit LIMIT, -l LIMIT                Maximum number of comments to download
  --language LANGUAGE, -a LANGUAGE       Language for YouTube generated text (e.g. en)
  --sort {0,1}, -s {0,1}                 Sort by: 0=popular, 1=recent (default: 1)
```

## Examples

Download comments using a YouTube URL:

```bash
yt-comment-dl "https://www.youtube.com/watch?v=ScMzIvxBSi4" --output ScMzIvxBSi4.json
```

Download comments using just the video ID:

```bash
yt-comment-dl ScMzIvxBSi4 --output ScMzIvxBSi4.json
```

Download the 50 most popular comments with pretty formatting:

```bash
yt-comment-dl ScMzIvxBSi4 --sort 0 --limit 50 --pretty
```

For YouTube IDs starting with `-` (dash), you may need to use quotes:

```bash
yt-comment-dl "-idwithdash"
```

## Usage as library

You can also use this script as a library. For instance, if you want to print out the 10 most popular comments for a particular YouTube video you can do the following:

```python
from itertools import islice
from yt_comment_dl import YoutubeCommentDownloader

downloader = YoutubeCommentDownloader()
comments = downloader.get_comments('ScMzIvxBSi4', sort_by=0)  # 0 = popular
for comment in islice(comments, 10):
    print(comment.to_dict())
```

## Output format

The output is a JSON array containing comment objects. Each comment has the following structure:

```json
[
  {
    "cid": "comment_id",
    "text": "Comment text",
    "time": "2 hours ago",
    "author": "Author Name",
    "channel": "author_channel_id",
    "votes": 42,
    "photo": "author_profile_photo_url",
    "heart": false,
    "reply": false,
    "time_parsed": 1234567890
  }
]
```

## License

MIT License - see [LICENSE](LICENSE) file for details
