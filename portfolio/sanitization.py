from __future__ import annotations

import bleach


ALLOWED_BLOG_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "br",
    "code",
    "div",
    "em",
    "figcaption",
    "figure",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "span",
    "strong",
    "ul",
]

ALLOWED_BLOG_ATTRIBUTES = {
    "*": ["class"],
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
}

ALLOWED_BLOG_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_rich_html(value: str) -> str:
    if not value:
        return ""

    cleaned = bleach.clean(
        value,
        tags=ALLOWED_BLOG_TAGS,
        attributes=ALLOWED_BLOG_ATTRIBUTES,
        protocols=ALLOWED_BLOG_PROTOCOLS,
        strip=True,
        strip_comments=True,
    )
    return bleach.linkify(cleaned, skip_tags=["pre", "code"])
