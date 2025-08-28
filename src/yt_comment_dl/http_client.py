"""HTTP client for YouTube API requests."""

from __future__ import print_function
import time
import requests
from .constants import USER_AGENT, YOUTUBE_CONSENT_URL


class YouTubeHTTPClient:
    """Handles HTTP requests to YouTube."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.session.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")

    def get_page(self, url):
        """Fetch a YouTube page."""
        return self.session.get(url)

    def handle_consent(self, response, youtube_url, hidden_input_parser):
        """Handle YouTube consent page if redirected."""
        if "consent" not in str(response.url):
            return response

        params = hidden_input_parser(response.text)
        params.update(
            {
                "continue": youtube_url,
                "set_eom": False,
                "set_ytc": True,
                "set_apyt": True,
            }
        )
        return self.session.post(YOUTUBE_CONSENT_URL, params=params)

    def ajax_request(self, endpoint, ytcfg, retries=5, sleep=20, timeout=60):
        """Make an AJAX request to YouTube API."""
        url = (
            "https://www.youtube.com" + endpoint["commandMetadata"]["webCommandMetadata"]["apiUrl"]
        )
        data = {
            "context": ytcfg["INNERTUBE_CONTEXT"],
            "continuation": endpoint["continuationCommand"]["token"],
        }

        for _ in range(retries):
            try:
                response = self.session.post(
                    url,
                    params={"key": ytcfg["INNERTUBE_API_KEY"]},
                    json=data,
                    timeout=timeout,
                )
                if response.status_code == 200:
                    return response.json()
                if response.status_code in [403, 413]:
                    return {}
            except requests.exceptions.Timeout:
                pass
            time.sleep(sleep)

        return {}
