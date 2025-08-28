"""Constants for YouTube comment downloader."""

# URLs
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={youtube_id}"
YOUTUBE_CONSENT_URL = "https://consent.youtube.com/save"

# Headers
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"

# Sort options
SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1

# Regex patterns
YT_CFG_RE = r"ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;"
YT_INITIAL_DATA_RE = r'(?:window\s*\[\s*["\']ytInitialData["\']\s*\]|ytInitialData)\s*=\s*({.+?})\s*;\s*(?:var\s+meta|</script|\n)'
YT_HIDDEN_INPUT_RE = r'<input\s+type="hidden"\s+name="([A-Za-z0-9_]+)"\s+value="([A-Za-z0-9_\-\.]*)"\s*(?:required|)\s*>'

# Target IDs for comment processing
COMMENT_TARGET_IDS = [
    "comments-section",
    "engagement-panel-comments-section",
    "shorts-engagement-panel-comments-section",
]
