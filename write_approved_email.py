#!/usr/bin/env python3
"""
Script to generate approved email from FSDS ticket JSON and template.
"""

import argparse
import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def main():
    """Main function with argparse CLI."""
    parser = argparse.ArgumentParser(
        description='Generate approved email from FSDS ticket JSON'
    )
    parser.add_argument(
        'fsds_number',
        type=int,
        help='FSDS ticket number (e.g., 189)'
    )

    args = parser.parse_args()

    # Construct JSON filename
    json_file = f"FSDS-{args.fsds_number}-info.json"
    template_file = "approved-template.md"

    # Check if files exist
    if not Path(json_file).exists():
        print(f"Error: JSON file '{json_file}' not found")
        sys.exit(1)

    if not Path(template_file).exists():
        print(f"Error: Template file '{template_file}' not found")
        sys.exit(1)

    try:
        # Read ticket info from JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            ticket_info = json.load(f)

        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template(template_file)

        # Render template
        approved_email = template.render(ticket_info)

        # Print to console
        print(approved_email)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{json_file}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()