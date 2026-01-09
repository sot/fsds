#!/usr/bin/env python3
"""
Script to extract ticket information from Jira HTML files.
"""

import argparse
import re
import subprocess
import sys

from bs4 import BeautifulSoup


def extract_ticket_info(html_content):
    """
    Extract ticket information from Jira HTML content.

    Args:
        html_content (str): HTML content of the Jira ticket page

    Returns:
        dict: Dictionary containing 'title', 'author', and 'fsds_number'
    """

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract document.title from JavaScript
    title_match = re.search(r'document\.title\s*=\s*"([^"]*)"', html_content)
    if not title_match:
        raise ValueError("Could not find document.title in HTML")

    full_title = title_match.group(1)

    # Parse FSDS number and clean title
    fsds_match = re.search(r'\[FSDS-(\d+)\]', full_title)
    if not fsds_match:
        raise ValueError("Could not extract FSDS number from title")

    fsds_number = int(fsds_match.group(1))

    # Extract title part (remove FSDS prefix and "- OCC Jira" suffix)
    title_part = re.sub(r'^\[FSDS-\d+\]\s*', '', full_title)
    title_part = re.sub(r'\s*-\s*OCC Jira$', '', title_part)
    title = title_part.strip()

    # Extract reporter name from definition list
    dt_reporter = soup.find('dt', string='Reporter:')
    if not dt_reporter:
        raise ValueError("Could not find Reporter field")

    dd_reporter = dt_reporter.find_next_sibling('dd')
    if not dd_reporter:
        raise ValueError("Could not find reporter data")

    # Get clean text from the dd element
    reporter_text = dd_reporter.get_text(strip=True)

    # Clean up the reporter name (remove extra whitespace and button text)
    reporter_lines = [line.strip() for line in reporter_text.split('\n') if line.strip()]
    # The name should be the first substantial text that looks like a person's name
    author = None
    for line in reporter_lines:
        words = line.split()
        # Look for a line with 2+ words that start with capitals (likely a person's name)
        if len(words) >= 2 and any(word[0].isupper() for word in words[:2]):
            author = line
            break

    if not author:
        # Fallback: just take the first non-empty line
        author = reporter_lines[0] if reporter_lines else "Unknown"

    return {
        'title': title,
        'author': author,
        'fsds_number': fsds_number
    }


def generate_review_email_html(ticket_info, template_file='email-template.md'):
    """
    Generate HTML review email from template and ticket info.

    Args:
        ticket_info (dict): Dictionary with title, author, fsds_number
        template_file (str): Path to email template file

    Returns:
        str: HTML formatted email content
    """
    import html
    from datetime import datetime, timedelta

    # Calculate review deadline (3 weekdays from today)
    today = datetime.now()
    weekdays_added = 0
    current_date = today

    while weekdays_added < 3:
        current_date += timedelta(days=1)
        # Monday=0, Sunday=6, so weekdays are 0-4
        if current_date.weekday() < 5:
            weekdays_added += 1

    review_deadline = current_date.strftime("%A %B %d").replace(" 0", " ")

    # Read template
    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()

    # Replace template variables
    email_text = template.replace('{{author}}', ticket_info['author'])
    email_text = email_text.replace('{{title}}', ticket_info['title'])
    email_text = email_text.replace('{{fsds_number}}', f"FSDS-{ticket_info['fsds_number']}")
    email_text = email_text.replace('{{review_deadline}}', review_deadline)

    # Convert to HTML while preserving whitespace and line breaks
    # Escape HTML entities first
    html_content = html.escape(email_text)

    # Convert leading spaces to non-breaking spaces to preserve indentation
    lines = html_content.split('\n')
    for i, line in enumerate(lines):
        # Count leading spaces and convert them to &nbsp;
        leading_spaces = len(line) - len(line.lstrip(' '))
        if leading_spaces > 0:
            lines[i] = '&nbsp;' * leading_spaces + line.lstrip(' ')
    html_content = '\n'.join(lines)

    # Convert markdown-style formatting to HTML
    # Handle **bold** text
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)

    # Handle [link text](url) markdown links
    html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)

    # Replace line breaks with <br> tags
    html_content = html_content.replace('\n', '<br>\n')

    # Wrap in basic HTML structure with default sans font and normal spacing
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>FSDS Review Request</title>
    <style>
        body {{
            font-family: Verdana, sans-serif;
            font-size: small;
            margin: 20px;
        }}
        a {{
            color: blue;
            text-decoration: underline;
        }}
        strong {{
            font-weight: bold;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    return full_html


def main():
    """Main function with argparse CLI."""
    parser = argparse.ArgumentParser(
        description='Extract ticket information from Jira HTML and generate review email'
    )
    parser.add_argument(
        'html_file',
        nargs='?',
        help='Path to Jira HTML file (if not provided, reads from STDIN)'
    )
    parser.add_argument(
        '--open',
        action='store_true',
        help='Automatically open the generated HTML file in browser'
    )

    args = parser.parse_args()

    # Read HTML content
    if args.html_file:
        try:
            with open(args.html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.html_file}' not found")
            sys.exit(1)
    else:
        # Read from STDIN
        html_content = sys.stdin.read()
        if not html_content.strip():
            print("Error: No HTML content provided via STDIN")
            sys.exit(1)

    try:
        info = extract_ticket_info(html_content)

        # Always show parsed information
        print(f"FSDS Number: {info['fsds_number']}")
        print(f"Title: {info['title']}")
        print(f"Author: {info['author']}")

        # Generate HTML email
        html_email = generate_review_email_html(info)
        output_file = f"review_email_FSDS-{info['fsds_number']}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_email)
        print(f"HTML email written to: {output_file}")

        # Open in browser if requested
        if args.open:
            subprocess.run(['open', output_file])

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()