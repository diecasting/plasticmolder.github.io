#!/usr/bin/env bash
# ==========================================================================
# init-site.sh — Interactive Site Initialization Script
# ==========================================================================
# Transforms the framework into a production website by customizing
# config files, schema data, and generating initial content.
#
# Usage: ./scripts/init-site.sh
# ==========================================================================

set -euo pipefail

FRAMEWORK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$FRAMEWORK_DIR"

echo "============================================"
echo "  Industrial Hugo SEO Framework"
echo "  Site Initialization Wizard"
echo "============================================"
echo ""

# --- Collect input ---
read -rp "Company Name [Example Manufacturing]: " COMPANY_NAME
COMPANY_NAME="${COMPANY_NAME:-Example Manufacturing}"

read -rp "Industry (e.g., Aluminum Die Casting) [Aluminum Die Casting]: " INDUSTRY
INDUSTRY="${INDUSTRY:-Aluminum Die Casting}"

read -rp "Country [CN]: " COUNTRY
COUNTRY="${COUNTRY:-CN}"

read -rp "Main Services (comma-separated) [aluminum-die-casting,cnc-machining]: " SERVICES
SERVICES="${SERVICES:-aluminum-die-casting,cnc-machining}"

read -rp "Contact Email [contact@example.com]: " EMAIL
EMAIL="${EMAIL:-contact@example.com}"

read -rp "Website URL [https://example.com/]: " WEBSITE_URL
WEBSITE_URL="${WEBSITE_URL:-https://example.com/}"

read -rp "City [Dongguan]: " CITY
CITY="${CITY:-Dongguan}"

read -rp "Province/State [Guangdong]: " REGION
REGION="${REGION:-Guangdong}"

echo ""
echo "============================================"
echo "  Configuration Summary"
echo "============================================"
echo "  Company:  $COMPANY_NAME"
echo "  Industry: $INDUSTRY"
echo "  Country:  $COUNTRY"
echo "  Services: $SERVICES"
echo "  Email:    $EMAIL"
echo "  URL:      $WEBSITE_URL"
echo "  Location: $CITY, $REGION"
echo "============================================"
read -rp "Proceed with these settings? [y/N]: " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo ">>> Updating configuration files..."

# --- Update hugo.toml ---
sed -i.bak "s|baseURL = \"https://example.com/\"|baseURL = \"$WEBSITE_URL\"|" config/_default/hugo.toml
sed -i.bak "s|title = \"Industrial Manufacturing Framework\"|title = \"$COMPANY_NAME\"|" config/_default/hugo.toml
rm -f config/_default/hugo.toml.bak

# --- Update params.toml ---
sed -i.bak "s|name = \"Your Company Name\"|name = \"$COMPANY_NAME\"|" config/_default/params.toml
sed -i.bak "s|email = \"contact@example.com\"|email = \"$EMAIL\"|g" config/_default/params.toml
sed -i.bak "s|copyright = \"Your Company Name. All rights reserved.\"|copyright = \"$COMPANY_NAME. All rights reserved.\"|" config/_default/params.toml
rm -f config/_default/params.toml.bak

# --- Update organization.toml ---
sed -i.bak "s|legal_name = \"Example Manufacturing Co., Ltd.\"|legal_name = \"$COMPANY_NAME\"|" data/schema/organization.toml
sed -i.bak "s|url = \"https://example.com/\"|url = \"$WEBSITE_URL\"|" data/schema/organization.toml
sed -i.bak "s|name = \"Example Manufacturing\"|name = \"$COMPANY_NAME\"|" data/schema/organization.toml
sed -i.bak "s|contact_email = \"contact@example.com\"|contact_email = \"$EMAIL\"|" data/schema/organization.toml
sed -i.bak "s|address_locality = \"City\"|address_locality = \"$CITY\"|" data/schema/organization.toml
sed -i.bak "s|address_region = \"Province/State\"|address_region = \"$REGION\"|" data/schema/organization.toml
sed -i.bak "s|address_country = \"CN\"|address_country = \"$COUNTRY\"|" data/schema/organization.toml
rm -f data/schema/organization.toml.bak

# --- Update locations.toml ---
sed -i.bak "s|address_locality = \"City\"|address_locality = \"$CITY\"|" data/schema/locations.toml
sed -i.bak "s|address_region = \"Province/State\"|address_region = \"$REGION\"|" data/schema/locations.toml
sed -i.bak "s|address_country = \"CN\"|address_country = \"$COUNTRY\"|" data/schema/locations.toml
sed -i.bak "s|url = \"https://example.com/\"|url = \"$WEBSITE_URL\"|" data/schema/locations.toml
rm -f data/schema/locations.toml.bak

echo ">>> Config files updated."

# --- Generate homepage if it doesn't exist ---
if [ ! -f "content/_index.md" ]; then
  echo ">>> Generating homepage..."
  cat > content/_index.md << 'HOMEPAGE'
---
title: "Home"
layout: "landing"
description: "Precision industrial manufacturing services."
sections:
  - hero
  - capabilities
  - process
  - industries
  - certifications
  - rfq
---
HOMEPAGE
fi

# --- Generate service pages ---
IFS=',' read -ra SERVICE_ARRAY <<< "$SERVICES"
for service in "${SERVICE_ARRAY[@]}"; do
  service=$(echo "$service" | xargs)  # trim whitespace
  service_dir="content/$(echo "$service" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
  if [ ! -d "$service_dir" ]; then
    echo ">>> Generating service page: $service"
    mkdir -p "$service_dir"
    cat > "$service_dir/index.md" << SERVICE_PAGE
---
title: "$(echo "$service" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')"
date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
draft: false
description: "Professional $(echo "$service" | tr '-' ' ') services with precision quality assurance."
---

## Overview

Professional $(echo "$service" | tr '-' ' ') services for industrial applications.

## Capabilities

- High-precision manufacturing
- Quality inspection and testing
- Custom solutions

## Get a Quote

{{< rfq_form >}}
SERVICE_PAGE
  fi
done

echo ""
echo "============================================"
echo "  Site initialization complete!"
echo "============================================"
echo ""
echo "  Next steps:"
echo "  1. Review and customize data/schema/*.toml"
echo "  2. Add your content to content/"
echo "  3. Add images to static/img/"
echo "  4. Build: hugo --environment production --gc --minify"
echo "  5. Deploy to GitHub Pages or your hosting provider"
echo ""
