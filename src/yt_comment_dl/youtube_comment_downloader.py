"""Main YouTube comment downloader class."""

from __future__ import print_function
from .constants import YOUTUBE_VIDEO_URL, SORT_BY_RECENT
from .http_client import YouTubeHTTPClient
from .parser import YouTubeParser
from .comment_processor import CommentProcessor


class YoutubeCommentDownloader:
    """Downloads comments from YouTube videos."""

    def __init__(self):
        self.http_client = YouTubeHTTPClient()
        self.parser = YouTubeParser()
        self.processor = CommentProcessor(self.parser)

    def get_comments(self, youtube_id, *args, **kwargs):
        """Get comments for a YouTube video by ID."""
        url = YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id)
        return self.get_comments_from_url(url, *args, **kwargs)

    def get_comments_from_url(self, youtube_url, sort_by=SORT_BY_RECENT, language=None, sleep=0.1):
        """Get comments from a YouTube URL."""
        # Fetch the page
        response = self.http_client.get_page(youtube_url)
        response = self.http_client.handle_consent(
            response, youtube_url, self.parser.extract_hidden_inputs
        )

        html = response.text

        # Extract configuration and initial data
        ytcfg = self.parser.extract_config(html)
        if not ytcfg:
            return  # Unable to extract configuration

        if language:
            ytcfg["INNERTUBE_CONTEXT"]["client"]["hl"] = language

        data = self.parser.extract_initial_data(html)
        if not data:
            return

        # Find initial comment section
        item_section = next(self.parser.search_dict(data, "itemSectionRenderer"), None)
        renderer = (
            next(self.parser.search_dict(item_section, "continuationItemRenderer"), None)
            if item_section
            else None
        )

        if not renderer:
            return  # Comments disabled

        # Get sort menu
        sort_menu = self._get_sort_menu(data, ytcfg)
        if not sort_menu or sort_by >= len(sort_menu):
            raise RuntimeError("Failed to set sorting")

        # Start processing comments
        continuations = [sort_menu[sort_by]["serviceEndpoint"]]

        while continuations:
            continuation = continuations.pop()
            response = self.http_client.ajax_request(continuation, ytcfg)

            if not response:
                break

            # Check for errors
            error = next(self.parser.search_dict(response, "externalErrorMessage"), None)
            if error:
                raise RuntimeError("Error returned from server: " + error)

            # Process continuations
            new_continuations = self.processor.process_continuations(response)
            continuations[:0] = new_continuations  # Prepend to list

            # Yield comments
            yield from self.processor.process_comments(response, sleep)

    def _get_sort_menu(self, data, ytcfg):
        """Extract sort menu from data, with fallback for community posts."""
        sort_menu = next(self.parser.search_dict(data, "sortFilterSubMenuRenderer"), {}).get(
            "subMenuItems", []
        )

        if not sort_menu:
            # No sort menu. Maybe this is a request for community posts?
            section_list = next(self.parser.search_dict(data, "sectionListRenderer"), {})
            continuations = list(self.parser.search_dict(section_list, "continuationEndpoint"))

            if continuations:
                # Retry with continuation
                data = self.http_client.ajax_request(continuations[0], ytcfg)
                if data:
                    sort_menu = next(
                        self.parser.search_dict(data, "sortFilterSubMenuRenderer"), {}
                    ).get("subMenuItems", [])

        return sort_menu
