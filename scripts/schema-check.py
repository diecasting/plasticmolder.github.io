#!/usr/bin/env python3
"""
schema-check.py — JSON-LD Schema Validation Script
=====================================================
Validates JSON-LD structured data in built HTML files:
- Extracts all <script type="application/ld+json"> blocks
- Validates JSON syntax
- Checks for duplicate @type on same page
- Reports schema types per page

Usage: python scripts/schema-check.py [public_dir]
Default public_dir: ./public
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import Counter


def extract_jsonld(html_content):
    """Extract all JSON-LD blocks from HTML."""
    pattern = r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>'
    matches = re.findall(pattern, html_content, re.DOTALL)
    blocks = []
    for match in matches:
        match = match.strip()
        if match:
            try:
                data = json.loads(match)
                blocks.append(data)
            except json.JSONDecodeError as e:
                blocks.append({"_parse_error": str(e), "_raw": match[:100]})
    return blocks


def check_file(filepath):
    issues = []
    schema_types = []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = extract_jsonld(content)

    for block in blocks:
        if isinstance(block, dict) and "_parse_error" in block:
            issues.append(f"JSON-LD parse error: {block['_parse_error']}")
            continue

        if isinstance(block, dict):
            schema_type = block.get("@type", "Unknown")
            schema_types.append(schema_type)
        elif isinstance(block, list):
            for item in block:
                if isinstance(item, dict):
                    schema_type = item.get("@type", "Unknown")
                    schema_types.append(schema_type)

    # Check for duplicate @type (excluding nested references)
    type_counts = Counter(schema_types)
    for stype, count in type_counts.items():
        if count > 1 and stype not in ("Organization",):
            # Organization may appear standalone + as publisher reference
            # But true duplicates (2 standalone Organization) are a problem
            issues.append(f"Duplicate @type: {stype} ({count} occurrences)")

    return issues, schema_types


def main():
    public_dir = sys.argv[1] if len(sys.argv) > 1 else "./public"
    if not os.path.isdir(public_dir):
        print(f"ERROR: Directory not found: {public_dir}")
        sys.exit(1)

    html_files = list(Path(public_dir).rglob("*.html"))
    if not html_files:
        print(f"WARNING: No HTML files found in {public_dir}")
        sys.exit(0)

    total_files = 0
    total_issues = 0
    files_with_issues = 0
    all_types = Counter()

    for filepath in sorted(html_files):
        rel_path = filepath.relative_to(".")
        total_files += 1
        issues, schema_types = check_file(str(filepath))

        for st in schema_types:
            all_types[st] += 1

        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            print(f"  {rel_path}")
            for issue in issues:
                print(f"    - {issue}")

    print(f"\n{'='*60}")
    print(f"Schema Check Summary")
    print(f"{'='*60}")
    print(f"  Files checked:      {total_files}")
    print(f"  Files with issues:  {files_with_issues}")
    print(f"  Total issues:       {total_issues}")
    print(f"\n  Schema types found:")
    for stype, count in sorted(all_types.items(), key=lambda x: -x[1]):
        print(f"    {stype}: {count}")

    if files_with_issues > 0:
        print(f"\n  STATUS: FAIL")
        sys.exit(1)
    else:
        print(f"\n  STATUS: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
