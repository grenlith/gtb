from datetime import datetime
from typing import List
from itertools import groupby
import re

MARKDOWN_LINK_URL_GROUP = 2
RAW_URL_GROUP = 3

def _extract_url_from_match(match: re.Match[str]) -> str:
    if match.group(MARKDOWN_LINK_URL_GROUP):
        return match.group(MARKDOWN_LINK_URL_GROUP)
    return match.group(RAW_URL_GROUP)

class NormalizedPost:
    def __init__(self) -> None:
        self.timestamp: datetime = datetime.min
        self.source_uri: str = ""
        self.source_app: str = ""
        self.author: str = ""
        self.text: str = ""
        self.tags: List[str] = [] # often empty

def format_links_in_text(text: str) -> str:
    markdown_link_pattern: str = r'\[([^\]]+)\]\(([^\)]+)\)'
    raw_url_pattern: str = r'(https?://[^\s]+)'

    # TODO: this needs more testing but i keep forgetting to post links
    combined_pattern: str = f'{markdown_link_pattern}|{raw_url_pattern}'

    result_lines: List[str] = []
    current_text: str = text
    last_end: int = 0

    for match in re.finditer(combined_pattern, current_text):
        before_text: str = current_text[last_end:match.start()].strip()
        if before_text:
            result_lines.append(before_text)
            result_lines.append("") # gemtext works like markdown here, i think

        url = _extract_url_from_match(match)
        result_lines.append(f"=> {url}")
        result_lines.append("")  # Blank line after link

        last_end = match.end()

    # Add any remaining text after the last link
    remaining_text: str = current_text[last_end:].strip()
    if remaining_text:
        result_lines.append(remaining_text)

    return "\n".join(result_lines)

def format_post_to_gemtext(post: NormalizedPost) -> str:
    lines = []

    if post.timestamp != datetime.min:
        date_str = post.timestamp.strftime("%H:%M:%S (%Z)")
        lines.append(f"=> {post.source_uri} {date_str}")
        lines.append("")
        
    if post.text:
        formatted_text = format_links_in_text(post.text)
        lines.append(formatted_text)
        lines.append("")
    
    if post.author:
        lines.append(f"post author: {post.author}")
        lines.append("")

    if post.tags and post.tags != ['']:
        lines.append("*tags used in this post:*")
        for tag in post.tags:
            if tag:
                lines.append(f"#{tag}")
        lines.append("")

    return "\n".join(lines)

def to_gemtext_list(posts: List[NormalizedPost]) -> List[str]:
    if not posts:
        return []

    # sort posts by timestamp
    sorted_posts = sorted(posts, key=lambda p: p.timestamp)

    # group posts by date
    result: List[str] = []
    for day, day_posts in groupby(sorted_posts, key=lambda p: p.timestamp.date()):
        day_post_list = list(day_posts)
        formatted_posts = [format_post_to_gemtext(post) for post in day_post_list]
        date_header = f"# {day.strftime('%Y-%m-%d')}\n\n"
        combined = date_header + "\n".join(formatted_posts)
        result.append(combined)

    return result

def to_gemtext(posts: List[NormalizedPost]) -> str:
    return "\n".join(to_gemtext_list(posts))
