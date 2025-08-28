"""Data models for YouTube comments."""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Comment:
    """Represents a YouTube comment."""

    cid: str
    text: str
    time: str
    author: str
    channel: str
    votes: str
    replies: int
    photo: str
    heart: bool
    reply: bool
    time_parsed: Optional[float] = None
    paid: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_payload(cls, comment_payload, toolbar_state, payments=None):
        """Create Comment from YouTube API payload."""
        properties = comment_payload["properties"]
        cid = properties["commentId"]
        author = comment_payload["author"]
        toolbar = comment_payload["toolbar"]

        comment = cls(
            cid=cid,
            text=properties["content"]["content"],
            time=properties["publishedTime"],
            author=author["displayName"],
            channel=author["channelId"],
            votes=toolbar["likeCountNotliked"].strip() or "0",
            replies=toolbar["replyCount"],
            photo=author["avatarThumbnailUrl"],
            heart=toolbar_state.get("heartState", "") == "TOOLBAR_HEART_STATE_HEARTED",
            reply="." in cid,
        )

        if payments and cid in payments:
            comment.paid = payments[cid]

        return comment
