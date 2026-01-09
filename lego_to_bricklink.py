#!/usr/bin/env python3
"""
LEGO Element ID to BrickLink Wanted List Converter

Ce script convertit une liste d'element IDs LEGO (depuis un manuel LEGO)
en fichier XML compatible avec BrickLink pour importer une Wanted List.

Usage:
    python lego_to_bricklink.py input.csv output.xml

Format CSV attendu (separateur: point-virgule):
    element_id;quantity
    4211221;1
    4585493;2
    ...

Requires:
    - BrickLink API credentials in environment variables or in the script
"""

import hmac
import hashlib
import base64
import time
import random
import string
import urllib.parse
import urllib.request
import json
import ssl
import sys
import os
from collections import defaultdict

# =============================================================================
# CONFIGURATION - BrickLink API Credentials
# =============================================================================
# Set environment variables before running:
#   export BRICKLINK_CONSUMER_KEY=...
#   export BRICKLINK_CONSUMER_SECRET=...
#   export BRICKLINK_TOKEN=...
#   export BRICKLINK_TOKEN_SECRET=...
#
# Or create a .env file and source it: source .env

CONSUMER_KEY = os.environ.get("BRICKLINK_CONSUMER_KEY", "")
CONSUMER_SECRET = os.environ.get("BRICKLINK_CONSUMER_SECRET", "")
TOKEN = os.environ.get("BRICKLINK_TOKEN", "")
TOKEN_SECRET = os.environ.get("BRICKLINK_TOKEN_SECRET", "")

# =============================================================================
# BrickLink API Functions
# =============================================================================

def generate_nonce(length=32):
    """Generate a random nonce for OAuth."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_signature(method, url, params, consumer_secret, token_secret):
    """Generate OAuth 1.0a signature."""
    sorted_params = sorted(params.items())
    param_string = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
    base_string = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()
    return signature


def make_bricklink_request(endpoint):
    """Make an authenticated request to the BrickLink API."""
    base_url = "https://api.bricklink.com/api/store/v1"
    url = f"{base_url}{endpoint}"
    method = "GET"

    oauth_params = {
        "oauth_consumer_key": CONSUMER_KEY,
        "oauth_token": TOKEN,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_nonce": generate_nonce(),
        "oauth_version": "1.0"
    }

    signature = generate_signature(method, url, oauth_params, CONSUMER_SECRET, TOKEN_SECRET)
    oauth_params["oauth_signature"] = signature

    auth_header = "OAuth " + ", ".join([
        f'{k}="{urllib.parse.quote(str(v), safe="")}"'
        for k, v in oauth_params.items()
    ])

    req = urllib.request.Request(url)
    req.add_header("Authorization", auth_header)
    req.add_header("Accept", "application/json")

    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": str(e), "code": e.code}
    except urllib.error.URLError as e:
        return {"error": str(e), "code": -1}


def get_element_mapping(element_id):
    """Get BrickLink part number and color from LEGO element ID."""
    result = make_bricklink_request(f"/item_mapping/{element_id}")

    if result.get("meta", {}).get("code") == 200:
        data = result.get("data", [])
        if data:
            item = data[0]
            return {
                "part_no": item.get("item", {}).get("no"),
                "color_id": item.get("color_id"),
                "element_id": element_id,
                "success": True
            }

    return {
        "element_id": element_id,
        "success": False,
        "error": result.get("error", "Unknown error")
    }


# =============================================================================
# CSV & XML Functions
# =============================================================================

def parse_csv(filename):
    """
    Parse CSV file with element IDs and quantities.
    Format: element_id;quantity (one per line)
    Returns dict: {element_id: total_quantity}
    """
    element_quantities = defaultdict(int)

    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                parts = line.split(';')
                if len(parts) >= 2:
                    element_id = parts[0].strip()
                    quantity = int(parts[1].strip())
                    element_quantities[element_id] += quantity
                else:
                    print(f"Warning: Line {line_num} invalid format: {line}")
            except ValueError as e:
                print(f"Warning: Line {line_num} parse error: {e}")

    return dict(element_quantities)


def generate_xml(parts):
    """Generate BrickLink XML from parts list."""
    xml_lines = ['<INVENTORY>']

    for part in parts:
        xml_lines.append('<ITEM>')
        xml_lines.append('<ITEMTYPE>P</ITEMTYPE>')
        xml_lines.append(f'<ITEMID>{part["part_no"]}</ITEMID>')
        xml_lines.append(f'<COLOR>{part["color_id"]}</COLOR>')
        xml_lines.append(f'<MINQTY>{part["quantity"]}</MINQTY>')
        xml_lines.append('</ITEM>')

    xml_lines.append('</INVENTORY>')
    return '\n'.join(xml_lines)


# =============================================================================
# Main
# =============================================================================

def main():
    # Check arguments
    if len(sys.argv) < 3:
        print("LEGO to BrickLink Wanted List Converter")
        print()
        print("Usage: python lego_to_bricklink.py <input.csv> <output.xml>")
        print()
        print("Example:")
        print("  python lego_to_bricklink.py missing_parts.csv wanted_list.xml")
        print()
        print("CSV format (semicolon-separated):")
        print("  element_id;quantity")
        print("  4211221;1")
        print("  4585493;2")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check API credentials
    if not CONSUMER_KEY or not CONSUMER_SECRET or not TOKEN or not TOKEN_SECRET:
        print("Error: BrickLink API credentials not configured.")
        print()
        print("Set environment variables:")
        print("  export BRICKLINK_CONSUMER_KEY=your_key")
        print("  export BRICKLINK_CONSUMER_SECRET=your_secret")
        print("  export BRICKLINK_TOKEN=your_token")
        print("  export BRICKLINK_TOKEN_SECRET=your_token_secret")
        print()
        print("Or create a .env file and run: source .env")
        print()
        print("Get your API keys at: https://www.bricklink.com/v2/api/register_consumer.page")
        sys.exit(1)

    # Parse CSV
    print(f"Reading {input_file}...")
    try:
        element_quantities = parse_csv(input_file)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    print(f"Found {len(element_quantities)} unique element IDs")
    print()

    # Query BrickLink API for each element
    print("Querying BrickLink API...")
    print("-" * 70)
    print(f"{'Element ID':<12} {'Part No':<12} {'Color':<8} {'Qty':<6} {'Status'}")
    print("-" * 70)

    parts = []
    errors = []

    for element_id, quantity in sorted(element_quantities.items()):
        mapping = get_element_mapping(element_id)

        if mapping["success"]:
            parts.append({
                "element_id": element_id,
                "part_no": mapping["part_no"],
                "color_id": mapping["color_id"],
                "quantity": quantity
            })
            print(f"{element_id:<12} {mapping['part_no']:<12} {mapping['color_id']:<8} {quantity:<6} OK")
        else:
            errors.append(element_id)
            print(f"{element_id:<12} {'???':<12} {'???':<8} {quantity:<6} ERROR")

        # Rate limiting - small delay between requests
        time.sleep(0.15)

    print("-" * 70)
    print(f"Success: {len(parts)} | Errors: {len(errors)}")
    print()

    # Generate XML
    if parts:
        xml_content = generate_xml(parts)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        print(f"XML saved to: {output_file}")
        print(f"Total parts: {len(parts)}")
        print(f"Total pieces: {sum(p['quantity'] for p in parts)}")
    else:
        print("No parts to export.")

    if errors:
        print()
        print(f"Warning: {len(errors)} element IDs could not be mapped:")
        for eid in errors:
            print(f"  - {eid}")


if __name__ == "__main__":
    main()
