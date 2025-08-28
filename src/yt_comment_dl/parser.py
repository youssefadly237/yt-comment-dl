"""Parsers for YouTube page data."""

import json
import re
import dateparser
from .constants import YT_CFG_RE, YT_INITIAL_DATA_RE, YT_HIDDEN_INPUT_RE


class YouTubeParser:
    """Handles parsing of YouTube page data."""

    @staticmethod
    def regex_search(text, pattern, group=1, default=None):
        """Search for regex pattern in text."""
        match = re.search(pattern, text)
        return match.group(group) if match else default

    @staticmethod
    def search_dict(partial, search_key):
        """Recursively search for a key in nested dict/list structure."""
        stack = [partial]
        while stack:
            current_item = stack.pop()
            if isinstance(current_item, dict):
                for key, value in current_item.items():
                    if key == search_key:
                        yield value
                    else:
                        stack.append(value)
            elif isinstance(current_item, list):
                stack.extend(current_item)

    def extract_config(self, html):
        """Extract YouTube configuration from HTML."""
        config_json = self.regex_search(html, YT_CFG_RE, default="")
        return json.loads(config_json) if config_json else None

    def extract_initial_data(self, html):
        """Extract initial YouTube data from HTML."""
        data_json = self.regex_search(html, YT_INITIAL_DATA_RE, default="")
        return json.loads(data_json) if data_json else None

    def extract_hidden_inputs(self, html):
        """Extract hidden form inputs as dict."""
        return dict(re.findall(YT_HIDDEN_INPUT_RE, html))

    def parse_comment_time(self, time_str):
        """Parse comment timestamp."""
        try:
            dt = dateparser.parse(time_str.split("(")[0].strip())
            return dt.timestamp() if dt else None
        except (AttributeError, TypeError):
            return None

    def extract_payments(self, response):
        """Extract payment information from response."""
        surface_payloads = list(self.search_dict(response, "commentSurfaceEntityPayload"))
        payments = {
            payload["key"]: next(self.search_dict(payload, "simpleText"), "")
            for payload in surface_payloads
            if "pdgCommentChip" in payload
        }

        if not payments:
            return {}

        # Map payload keys to comment IDs
        view_models = [
            vm["commentViewModel"] for vm in self.search_dict(response, "commentViewModel")
        ]
        surface_keys = {
            vm["commentSurfaceKey"]: vm["commentId"]
            for vm in view_models
            if "commentSurfaceKey" in vm
        }

        return {
            surface_keys[key]: payment for key, payment in payments.items() if key in surface_keys
        }

    def extract_toolbar_states(self, response):
        """Extract toolbar states from response."""
        toolbar_payloads = list(self.search_dict(response, "engagementToolbarStateEntityPayload"))
        return {payload["key"]: payload for payload in toolbar_payloads}
