import requests
import re
from transformer import NormalizedPost
from datetime import datetime
from zoneinfo import ZoneInfo
from config_parser import Collector, Options
from typing import List, Any, Dict
from markdownify import markdownify as md

DID_MINIDOC = "https://slingshot.microcosm.blue/xrpc/com.bad-example.identity.resolveMiniDoc?identifier="
BLUESKY_LEXICON = "app.bsky.feed.post"
KIBUN_LEXICON = "social.kibun.status"

def parse_iso_utc_to_timezone(timestamp_str: str, target_timezone: str) -> datetime:
    utc_time = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=ZoneInfo("UTC"))
    return utc_time.astimezone(ZoneInfo(target_timezone))

def find_tags(post: str) -> List[str]:
    hashtag_pattern = r'#(\w+)'
    matches = re.findall(hashtag_pattern, post)
    return matches if matches else []        

def collect(source_config: Collector, opts: Options) -> List[NormalizedPost]:
    posts: List[NormalizedPost] = []

    collectors_map = {
        "bluesky": collect_bluesky,
        "kibun": collect_kibun,
        "mastodon": collect_mastodon
    }

    if handler := collectors_map.get(source_config.collector_type):
        posts.extend(handler(source_config, opts))

    return posts

def collect_mastodon(collector_config: Collector, opts: Options) -> List[NormalizedPost]:
    acct_data = collector_config.handle.split('@')
    r = requests.get(f"https://{acct_data[1]}/api/v1/accounts/"
                         f"lookup?acct={acct_data[0]}")
    r.raise_for_status()
    record = r.json()
    user_id = record["id"]

    r = requests.get(f"https://{acct_data[1]}/api/v1/accounts/{user_id}"
                     "/statuses?exclude_replies=true&exclude_reblogs=true"
                     f"&limit={collector_config.post_limit}")

    r.raise_for_status()
    records = r.json()
    verified_posts: List[Dict[Any,Any]] = []
    for record in records:
        if(not record["in_reply_to_id"] and not record["reblog"]):
            verified_posts.append(record)

    return transform_mastodon(verified_posts, collector_config, opts)

    
def collect_bluesky(collector_config: Collector, opts: Options) -> List[NormalizedPost]:
    r = requests.get(f"{DID_MINIDOC}{collector_config.handle}")
    r.raise_for_status()
    at_doc = r.json()

    r = requests.get(f"{at_doc["pds"]}/xrpc/"
                      f"com.atproto.repo.listRecords?repo={at_doc["did"]}"
                      f"&collection={BLUESKY_LEXICON}&limit={collector_config.post_limit}")

    r.raise_for_status()
    records = r.json()
    verified_posts: List[Dict[Any,Any]] = []
    for record in records['records']:
        if not ('embed' in record['value'].keys() or 'reply' in record['value'].keys()):
            verified_posts.append(record)

    return transform_bluesky(verified_posts, collector_config, opts)

def collect_kibun(collector_config: Collector, opts: Options) -> List[NormalizedPost]:
    r = requests.get(f"{DID_MINIDOC}{collector_config.handle}")
    r.raise_for_status()
    at_doc = r.json()

    r = requests.get(f"{at_doc["pds"]}/xrpc/"
                      f"com.atproto.repo.listRecords?repo={at_doc["did"]}"
                      f"&collection={KIBUN_LEXICON}&limit={collector_config.post_limit}")

    r.raise_for_status()
    records = r.json()
    verified_posts: List[Dict[Any,Any]] = []
    for record in records["records"]:
        verified_posts.append(record)

    return transform_kibun(verified_posts, collector_config, opts)

def transform_bluesky(posts: List[Dict[Any,Any]], collector_config: Collector, opts: Options) -> List[NormalizedPost]:
    NormalizedPosts: List[NormalizedPost] = []

    for post in posts:
        np: NormalizedPost = NormalizedPost()

        np.source_app = "bluesky"
        np.timestamp = parse_iso_utc_to_timezone(post["value"]["createdAt"], opts.timezone)

        at_uri = post["uri"]
        np.source_uri = at_uri.replace("at://", "https://reddwarf.app/profile/").replace("/app.bsky.feed.post/", "/post/")

        np.author = f"{collector_config.handle} (bluesky)"
        np.text = post["value"]["text"]
        np.tags.extend(find_tags(np.text))

        NormalizedPosts.append(np)

    return NormalizedPosts

def transform_mastodon(posts: List[Dict[Any,Any]], collector_config: Collector, opts: Options) -> List[NormalizedPost]:
    NormalizedPosts: List[NormalizedPost] = []

    for post in posts:
        np: NormalizedPost = NormalizedPost()

        np.source_app = "mastodon"
        np.timestamp = parse_iso_utc_to_timezone(post["created_at"], opts.timezone)
        np.source_uri = post["url"]
        np.author = f"{post["account"]["username"]} (mastodon)"
        np.text = md(post["content"], convert=['h1','h2','h3','a','b','i','em','br','p'])
        np.tags.extend(find_tags(np.text))

        NormalizedPosts.append(np)

    return NormalizedPosts

def transform_kibun(posts: List[Dict[Any,Any]], collector_config: Collector, opts: Options) -> List[NormalizedPost]:
    NormalizedPosts: List[NormalizedPost] = []

    for post in posts:
        np: NormalizedPost = NormalizedPost()

        np.source_app = "kibun"
        np.timestamp = parse_iso_utc_to_timezone(post["value"]["createdAt"], opts.timezone)
        np.source_uri = "https://www.kibun.social/"
        np.author = f"{collector_config.handle} (kibun)"
        np.text = f"{post["value"]['emoji']} | {post["value"]['text']}"
        np.tags.extend(find_tags(np.text))

        NormalizedPosts.append(np)

    return NormalizedPosts

