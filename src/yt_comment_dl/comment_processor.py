"""Comment processing logic."""

import time
from .constants import COMMENT_TARGET_IDS
from .models import Comment


class CommentProcessor:
    """Handles processing of comment data from API responses."""

    def __init__(self, parser):
        self.parser = parser

    def process_continuations(self, response):
        """Extract continuation endpoints from response."""
        continuations = []
        actions = list(self.parser.search_dict(response, "reloadContinuationItemsCommand")) + list(
            self.parser.search_dict(response, "appendContinuationItemsAction")
        )

        for action in actions:
            target_id = action.get("targetId", "")

            for item in action.get("continuationItems", []):
                if target_id in COMMENT_TARGET_IDS:
                    # Process continuations for comments and replies
                    continuations.extend(self.parser.search_dict(item, "continuationEndpoint"))

                elif (
                    target_id.startswith("comment-replies-item")
                    and "continuationItemRenderer" in item
                ):
                    # Process 'Show more replies' button
                    button_renderer = next(self.parser.search_dict(item, "buttonRenderer"), None)
                    if button_renderer and "command" in button_renderer:
                        continuations.append(button_renderer["command"])

        return continuations

    def process_comments(self, response, sleep=0.1):
        """Process comments from API response."""
        # Extract payments and toolbar states
        payments = self.parser.extract_payments(response)
        toolbar_states = self.parser.extract_toolbar_states(response)

        # Process comments in reverse order
        comment_payloads = list(self.parser.search_dict(response, "commentEntityPayload"))

        for comment_payload in reversed(comment_payloads):
            properties = comment_payload["properties"]
            toolbar_state = toolbar_states.get(properties["toolbarStateKey"], {})

            comment = Comment.from_payload(comment_payload, toolbar_state, payments)

            # Parse timestamp
            parsed_time = self.parser.parse_comment_time(comment.time)
            if parsed_time:
                comment.time_parsed = parsed_time

            yield comment

        if sleep > 0:
            time.sleep(sleep)
