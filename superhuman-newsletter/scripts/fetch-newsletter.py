#!/usr/bin/env python3
"""
Fetch full post content from Superhuman AI (superhuman.ai) and
The Code (codenewsletter.ai) newsletters. Scrapes public Beehiiv sites.

Usage:
  python3 fetch-newsletter.py --source superhuman --count 7
  python3 fetch-newsletter.py --source code --count 5
"""

import argparse
import json
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

# ─── Config ──────────────────────────────────────────────────────────

SOURCES = {
    "superhuman": {
        "base_url": "https://www.superhuman.ai",
        "default_count": 7,
        "max_count": 30,
        "default_author": "Zain Kahn",
        "paginated": True,
    },
    "code": {
        "base_url": "https://codenewsletter.ai",
        "default_count": 5,
        "max_count": 9,
        "default_author": "The Code team",
        "paginated": False,
    },
}

FETCH_DELAY_MS = 300
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# ─── HTTP Helpers ────────────────────────────────────────────────────

def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ─── HTML → Markdown Converter ───────────────────────────────────────

class MarkdownConverter(HTMLParser):
    """Convert HTML to Markdown. Handles the Beehiiv content structure."""

    def __init__(self):
        super().__init__()
        self.output = []
        self.stack = []
        self.list_depth = 0
        self.in_pre = False
        self.pre_content = []
        self.skip_until_close = None
        self.link_text = ""
        self.link_href = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag_lower = tag.lower()

        if self.skip_until_close:
            return

        # Elements to skip entirely
        if tag_lower in ("script", "style", "noscript", "form", "button"):
            self.skip_until_close = tag_lower
            return

        if tag_lower == "pre":
            self.in_pre = True
            self.pre_content = []
            return

        if self.in_pre:
            return

        if tag_lower in ("h1", "h2", "h3", "h4"):
            level = int(tag_lower[1])
            self._emit_block()
            self.stack.append({"tag": tag_lower, "prefix": "#" * level + " "})
        elif tag_lower == "p":
            self._emit_block()
            self.stack.append({"tag": "p", "prefix": ""})
        elif tag_lower == "li":
            self._emit_block()
            indent = "  " * max(0, self.list_depth - 1)
            self.stack.append({"tag": "li", "prefix": indent + "- "})
        elif tag_lower in ("ul", "ol"):
            self._emit_block()
            self.list_depth += 1
        elif tag_lower == "blockquote":
            self._emit_block()
            self.stack.append({"tag": "blockquote", "prefix": "> "})
        elif tag_lower == "br":
            self.output.append("\n")
        elif tag_lower in ("strong", "b"):
            self.output.append("**")
        elif tag_lower in ("em", "i"):
            self.output.append("*")
        elif tag_lower == "code":
            if self.in_pre:
                return
            self.output.append("`")
        elif tag_lower == "a":
            self.link_href = attrs_dict.get("href", "")
            self.output.append("[")
        elif tag_lower == "img":
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "")
            if src:
                self._emit_block()
                self.output.append(f"![{alt}]({src})\n")
        elif tag_lower == "hr":
            self._emit_block()
            self.output.append("\n---\n")

    def handle_endtag(self, tag):
        tag_lower = tag.lower()

        if self.skip_until_close:
            if tag_lower == self.skip_until_close:
                self.skip_until_close = None
            return

        if tag_lower == "pre":
            self.in_pre = False
            self._emit_block()
            content = "".join(self.pre_content)
            self.output.append(f"```\n{content}\n```\n")
            self.pre_content = []
            return

        if self.in_pre:
            return

        if tag_lower in ("h1", "h2", "h3", "h4", "p", "li", "blockquote"):
            self._emit_block()
        elif tag_lower in ("ul", "ol"):
            self.list_depth = max(0, self.list_depth - 1)
            self._emit_block()
        elif tag_lower in ("strong", "b"):
            self.output.append("**")
        elif tag_lower in ("em", "i"):
            self.output.append("*")
        elif tag_lower == "code":
            if not self.in_pre:
                self.output.append("`")
        elif tag_lower == "a":
            text = self.link_text.strip() if self.link_text else self.link_href
            self.output.append(f"]({self.link_href})")
            self.link_text = ""
            self.link_href = ""

    def handle_data(self, data):
        if self.skip_until_close:
            return
        if self.in_pre:
            self.pre_content.append(data)
            return
        if self.link_href and not self.link_text:
            self.link_text = data
        self.output.append(data.strip())

    def handle_entityref(self, name):
        entities = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}
        self.output.append(entities.get(name, f"&{name};"))

    def _emit_block(self):
        while self.stack:
            self.stack.pop()
            self.output.append("\n\n")

    def get_markdown(self):
        self._emit_block()
        raw = "".join(self.output)
        # Normalize whitespace
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        raw = re.sub(r" +\n", "\n", raw)
        raw = re.sub(r"\n +", "\n", raw)
        return raw.strip()


def html_to_markdown(html):
    converter = MarkdownConverter()
    converter.feed(html)
    return converter.get_markdown()


# ─── Metadata Extraction ─────────────────────────────────────────────

def extract_jsonld_meta(html):
    """Extract metadata from JSON-LD script tags."""
    meta = {}
    for match in re.finditer(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        html, re.DOTALL | re.IGNORECASE
    ):
        try:
            data = json.loads(match.group(1))
            if isinstance(data, dict):
                if data.get("headline"):
                    meta["title"] = data["headline"]
                if data.get("datePublished"):
                    meta["date"] = data["datePublished"]
                if data.get("description"):
                    meta["description"] = data["description"]
                if data.get("image", {}).get("url"):
                    meta["image"] = data["image"]["url"]
                if data.get("author", {}).get("name"):
                    meta["author"] = data["author"]["name"]
        except (json.JSONDecodeError, KeyError):
            continue
    return meta


def extract_og_meta(html):
    """Fallback: extract Open Graph meta tags."""
    meta = {}
    for match in re.finditer(
        r'<meta\s[^>]*property="og:(title|description|image)"[^>]*content="([^"]*)"',
        html, re.IGNORECASE
    ):
        prop, value = match.group(1), match.group(2)
        meta[prop] = value
    # h1 fallback for title
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if h1_match:
        meta["h1"] = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()
    return meta


# ─── Content Block Extraction ────────────────────────────────────────

def extract_content_html(html):
    """Extract the inner HTML of #content-blocks or fallback selectors."""
    for selector in [r'id="content-blocks"', r'class="[^"]*rendered-post[^"]*"']:
        # Find the tag containing this attribute
        match = re.search(
            r'<\w+\s[^>]*' + selector + r'[^>]*>(.*?)(?=<(script|style|nav|footer))',
            html, re.DOTALL | re.IGNORECASE
        )
        if match:
            content = match.group(1)
            # Close at the matching parent tag end if possible
            # For id="content-blocks" divs, find the closing </div> that's at the right nesting
            # Simpler approach: find the first matching closing tag after our start point
            # We'll use a regex to find the start of #content-blocks and capture until the next major section
            return content

    # Fallback: try to find main content area
    for tag in ("main", "article", "body"):
        match = re.search(
            rf"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.DOTALL | re.IGNORECASE
        )
        if match:
            return match.group(1)

    return html


def extract_content_block_html(html):
    """Extract just the #content-blocks div content using tag balancing."""
    # Find the opening tag
    start_match = re.search(r'id="content-blocks"[^>]*>', html, re.IGNORECASE)
    if not start_match:
        return None

    start_pos = start_match.end()
    tag_match = re.match(r'<(\w+)', start_match.group(0))
    if not tag_match:
        # The match is from an attribute, need to find the actual tag
        # Look backwards for the opening tag
        before = html[max(0, start_match.start() - 100):start_match.start()]
        tag_find = re.search(r'<(\w+)\s[^>]*$', before)
        if not tag_find:
            return None
        tag_name = tag_find.group(1)
    else:
        tag_name = tag_match.group(1)

    # Walk forward counting nesting depth
    depth = 1
    pos = start_pos
    open_pat = re.compile(rf'<{tag_name}\b', re.IGNORECASE)
    close_pat = re.compile(rf'</{tag_name}>', re.IGNORECASE)

    while depth > 0 and pos < len(html):
        next_open = open_pat.search(html, pos)
        next_close = close_pat.search(html, pos)

        if next_close is None:
            break

        if next_open and next_open.start() < next_close.start():
            depth += 1
            pos = next_open.end()
        else:
            depth -= 1
            if depth == 0:
                return html[start_pos:next_close.start()]
            pos = next_close.end()

    return html[start_pos:pos]


# ─── Content Cleaning ────────────────────────────────────────────────

def strip_noise_elements(html):
    """Remove common noise elements from newsletter HTML."""
    noise_tags = (
        r"<(script|style|noscript|nav|header|footer|form|button)\b.*?</\1>",
    )
    for pattern in noise_tags:
        html = re.sub(pattern, "", html, flags=re.DOTALL | re.IGNORECASE)

    # Remove elements by class name patterns (subscribe, share, feedback, poll, ads)
    for cls in ("subscribe", "share", "follow", "feedback", "poll", "advertisement"):
        html = re.sub(
            rf'<\w+\s[^>]*class="[^"]*{cls}[^"]*"[^>]*>.*?</\w+>',
            "", html, flags=re.DOTALL | re.IGNORECASE
        )

    # Remove sponsor paragraphs/headings
    sponsor_pat = r"(presented by|sponsored by|advertisement)\b"
    for tag in ("h1", "h2", "h3", "h4", "h5", "p"):
        html = re.sub(
            rf'<{tag}\b[^>]*>.*?{sponsor_pat}.*?</{tag}>',
            "", html, flags=re.DOTALL | re.IGNORECASE
        )

    return html


# ─── Listing Scraping ────────────────────────────────────────────────

def scrape_listings_superhuman(html, base_url):
    """Scrape post listings from Superhuman AI homepage/archive."""
    listings = []
    seen = set()

    # Find all /p/ links
    for match in re.finditer(r'<a\s[^>]*href="(/p/[^"]*)"[^>]*>', html):
        href = match.group(1)
        if href in seen:
            continue
        seen.add(href)

        slug = href[3:]  # strip "/p/"
        post_url = urljoin(base_url, href)

        # Get surrounding context for title and date
        # Look for h2 in the surrounding card
        link_start = match.start()
        context = html[max(0, link_start - 2000):min(len(html), link_start + 500)]

        # Title: look for h2 nearby
        title_match = re.search(r"<h2[^>]*>(.*?)</h2>", context, re.DOTALL | re.IGNORECASE)
        if title_match:
            title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        else:
            # Try img alt
            img_match = re.search(r'<img[^>]*alt="([^"]*)"[^>]*>', context, re.IGNORECASE)
            title = img_match.group(1).strip() if img_match else slug.replace("-", " ")

        # Date: first span in the card
        date_match = re.search(r"<span[^>]*>(.*?)</span>", context, re.DOTALL | re.IGNORECASE)
        raw_date = re.sub(r"<[^>]+>", "", date_match.group(1)).strip() if date_match else ""

        listings.append({"title": title, "date": raw_date, "url": post_url, "slug": slug})

    return listings


def scrape_listings_code(html, base_url):
    """Scrape post listings from The Code archive page."""
    listings = []
    seen = set()

    for match in re.finditer(r'<a\s[^>]*href="(/p/[^"]*)"[^>]*>', html):
        href = match.group(1)
        if href in seen:
            continue
        seen.add(href)

        slug = href[3:]
        post_url = urljoin(base_url, href)

        # Get context around the link
        link_start = match.start()
        context = html[max(0, link_start - 1000):min(len(html), link_start + 2000)]

        # Title from h3
        title_match = re.search(r"<h3[^>]*>(.*?)</h3>", context, re.DOTALL | re.IGNORECASE)
        if title_match:
            title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        else:
            title = slug.replace("-", " ")

        # Date from first p
        date_match = re.search(r"<p[^>]*>(.*?)</p>", context, re.DOTALL | re.IGNORECASE)
        raw_date = re.sub(r"<[^>]+>", "", date_match.group(1)).strip() if date_match else ""

        listings.append({"title": title, "date": raw_date, "url": post_url, "slug": slug})

    return listings


# ─── Post Content Scraping ───────────────────────────────────────────

def scrape_post(html, listing, default_author):
    """Extract full post content from a single post page."""
    # Metadata
    jsonld = extract_jsonld_meta(html)
    og = extract_og_meta(html)

    title = jsonld.get("title") or og.get("title") or og.get("h1") or listing["title"]
    date_str = jsonld.get("date") or listing["date"]
    description = jsonld.get("description") or og.get("description", "")
    image = jsonld.get("image") or og.get("image", "")
    author = jsonld.get("author") or default_author

    # Format date nicely
    if date_str and "T" in date_str:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            date_str = dt.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            pass

    # Content body
    content_html = extract_content_block_html(html)
    if not content_html:
        content_html = extract_content_html(html)

    content_html = strip_noise_elements(content_html)
    markdown = html_to_markdown(content_html)

    # External links
    external_links = []
    seen_links = set()
    internal_domains = ("superhuman.ai", "codenewsletter.ai", "beehiiv.com")
    social_domains = ("twitter.com/intent", "facebook.com/sharer", "linkedin.com/sharing")

    for link_match in re.finditer(
        r'<a\s[^>]*href="([^"#][^"]*)"[^>]*>(.*?)</a>',
        content_html, re.DOTALL | re.IGNORECASE
    ):
        href = link_match.group(1)
        text = re.sub(r"<[^>]+>", "", link_match.group(2)).strip()
        if (href and text and href not in seen_links
                and not any(d in href for d in internal_domains)
                and not any(d in href for d in social_domains)):
            seen_links.add(href)
            external_links.append({"text": text, "url": href})

    return {
        "title": title,
        "date": date_str,
        "author": author,
        "url": listing["url"],
        "subtitle": description,
        "content_markdown": markdown,
        "external_links": external_links,
        "featured_image": image or None,
    }


# ─── Format Output ───────────────────────────────────────────────────

def format_digest(posts, source_name, source_url):
    from datetime import datetime
    divider = "\n\n" + "─" * 80 + "\n\n"
    fetched_at = datetime.now().strftime("%A, %B %d, %Y")

    label = {
        "superhuman": "Superhuman AI Newsletter",
        "code": "The Code Newsletter",
    }.get(source_name, source_name.capitalize())

    header = (
        f"# {label} — {len(posts)} Most Recent Posts\n"
        f"Compiled: {fetched_at}\n"
        f"\n"
        f"Full content of each post is included below. Use this to produce a weekly digest\n"
        f"with combined top stories, must-read links, and a reference back to each source URL.\n"
    )

    sections = []
    for i, post in enumerate(posts):
        meta_lines = [
            f"## [Post {i + 1}/{len(posts)}] {post['title']}",
            f"**Date:** {post['date']}  |  **Author:** {post['author']}",
            f"**Source:** <{post['url']}>",
        ]
        if post.get("subtitle"):
            meta_lines.append(f"**Summary:** {post['subtitle']}")
        if post.get("featured_image"):
            meta_lines.append(f"\n![Featured Image]({post['featured_image']})\n")

        links = ""
        if post.get("external_links"):
            links = "\n\n**Links referenced in this post:**\n" + "\n".join(
                f"- [{l['text']}]({l['url']})" for l in post["external_links"]
            )

        sections.append("\n".join(meta_lines) + "\n\n" + post["content_markdown"] + links)

    return header + divider + divider.join(sections)


# ─── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch newsletter posts from Beehiiv-hosted sites.")
    parser.add_argument("--source", choices=["superhuman", "code"], required=True)
    parser.add_argument("--count", type=int, default=None)
    args = parser.parse_args()

    cfg = SOURCES[args.source]
    count = args.count or cfg["default_count"]
    count = max(1, min(count, cfg["max_count"]))

    print(f"Fetching {count} posts from {cfg['base_url']}...", file=sys.stderr)

    # Step 1: Collect listing URLs
    listings = []
    if cfg["paginated"]:
        page = 1
        while len(listings) < count:
            url = cfg["base_url"] if page == 1 else f"{cfg['base_url']}/archive?page={page}"
            html = fetch_html(url)
            batch = scrape_listings_superhuman(html, cfg["base_url"])
            if not batch:
                break
            listings.extend(batch)
            page += 1
            if len(listings) >= count:
                break
            time.sleep(FETCH_DELAY_MS / 1000)
    else:
        html = fetch_html(f"{cfg['base_url']}/archive")
        listings = scrape_listings_code(html, cfg["base_url"])

    listings = listings[:count]

    if not listings:
        print(f"No posts found on {cfg['base_url']}. Site may be unavailable.", file=sys.stderr)
        sys.exit(1)

    # Step 2: Fetch each post
    posts = []
    for i, listing in enumerate(listings):
        print(f"  [{i + 1}/{len(listings)}] {listing['title']}", file=sys.stderr)
        try:
            html = fetch_html(listing["url"])
            post = scrape_post(html, listing, cfg["default_author"])
            posts.append(post)
        except Exception as e:
            print(f"  ✗ Failed: {e}", file=sys.stderr)
            posts.append({
                "title": listing["title"],
                "date": listing["date"],
                "author": cfg["default_author"],
                "url": listing["url"],
                "subtitle": "",
                "content_markdown": f"_Could not fetch content: {e}_",
                "external_links": [],
                "featured_image": None,
            })

        if i < len(listings) - 1:
            time.sleep(FETCH_DELAY_MS / 1000)

    print(format_digest(posts, args.source, cfg["base_url"]))


if __name__ == "__main__":
    main()
