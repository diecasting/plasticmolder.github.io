#!/usr/bin/env python3
"""
seo-check.py — SEO Audit Script for Hugo Sites
==================================================
Checks built HTML files for common SEO issues:
- Missing <title> tags
- Missing meta description
- Missing canonical link
- Missing Open Graph tags
- Missing h1 tag
- Multiple h1 tags
- Empty alt attributes on images

Usage: python scripts/seo-check.py [public_dir]
Default public_dir: ./public
"""

import os
import re
import sys
from pathlib import Path
from html.parser import HTMLParser


class SEOChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.description = None
        self.canonical = None
        self.og_title = None
        self.og_description = None
        self.h1_count = 0
        self.images_without_alt = 0
        self.total_images = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = attrs_dict.get("name", "")
            property_attr = attrs_dict.get("property", "")
            if name == "description":
                self.description = attrs_dict.get("content", "")
            if property_attr == "og:title":
                self.og_title = attrs_dict.get("content", "")
            if property_attr == "og:description":
                self.og_description = attrs_dict.get("content", "")
        elif tag == "link":
            if attrs_dict.get("rel") == "canonical":
                self.canonical = attrs_dict.get("href", "")
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "img":
            self.total_images += 1
            alt = attrs_dict.get("alt", "")
            if not alt:
                self.images_without_alt += 1

    def handle_data(self, data):
        if hasattr(self, "_in_title") and self._in_title:
            self.title = data.strip()
            self._in_title = False


def check_file(filepath):
    issues = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        checker = SEOChecker()
        checker.feed(content)

        if not checker.title:
            issues.append("Missing <title> tag")
        if not checker.description:
            issues.append("Missing meta description")
        if not checker.canonical:
            issues.append("Missing canonical link")
        if not checker.og_title:
            issues.append("Missing og:title")
        if checker.h1_count == 0:
            issues.append("Missing h1 tag")
        elif checker.h1_count > 1:
            issues.append(f"Multiple h1 tags ({checker.h1_count})")
        if checker.images_without_alt > 0:
            issues.append(f"Images without alt: {checker.images_without_alt}/{checker.total_images}")
    except Exception as e:
        issues.append(f"Parse error: {e}")
    return issues


def main():
    public_dir = sys.argv[1] if len(sys.argv) > 1 else "./public"
    if not os.path.isdir(public_dir):
        print(f"ERROR: Directory not found: {public_dir}")
        sys.exit(1)

    html_files = list(Path(public_dir).rglob("*.html"))
    if not html_files:
        print(f"WARNING: No HTML files found in {public_dir}")
        sys.exit(0)

    # Skip pagination redirect pages (page/1/index.html)
    html_files = [f for f in html_files if "/page/1/" not in str(f).replace("\\", "/")]

    total_files = 0
    total_issues = 0
    files_with_issues = 0

    for filepath in sorted(html_files):
        rel_path = filepath.relative_to(".")
        total_files += 1
        issues = check_file(str(filepath))
        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            print(f"  {rel_path}")
            for issue in issues:
                print(f"    - {issue}")

    print(f"\n{'='*60}")
    print(f"SEO Check Summary")
    print(f"{'='*60}")
    print(f"  Files checked:    {total_files}")
    print(f"  Files with issues: {files_with_issues}")
    print(f"  Total issues:     {total_issues}")

    if files_with_issues > 0:
        print(f"\n  STATUS: FAIL")
        sys.exit(1)
    else:
        print(f"\n  STATUS: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
