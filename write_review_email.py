#!/usr/bin/env python3
"""
Script to get ticket information from Jira API and generate review emails.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from jira import JIRA


def init_jira_connection():
    "Initializer and return a Jira connection object"
    JIRA_SERVER = "https://occ-cfa.cfa.harvard.edu/"
    token_auth = (Path.home() / "jira_api_token.txt").read_text().strip()
    jira = JIRA(
        server=JIRA_SERVER,
        token_auth=token_auth,
        timeout=60,
    )

    print(f"Connected as: {jira.current_user()} to {JIRA_SERVER}")
    return jira


def get_jira_issue(jira, fsds_number):
    """Retrieve Jira issue object for given FSDS number.

    Args:
        jira (JIRA): Authenticated JIRA connection object
        fsds_number (int): FSDS ticket number
    """
    issue_key = f"FSDS-{fsds_number}"
    try:
        issue = jira.issue(issue_key)
        return issue
    except Exception as e:
        print(f"Error retrieving issue {issue_key}: {e}")
        sys.exit(1)

def get_title_reporter_from_issue(issue):
    """Extract title and reporter from Jira issue object.

    Args:
        issue (JIRA Issue): Jira issue object
    """
    title = issue.fields.summary
    reporter = issue.fields.reporter.displayName
    return title, reporter


def get_ticket_info_from_jira(fsds_number):
    """
    Get ticket information from Jira API using FSDS number.

    Args:
        fsds_number (int): FSDS ticket number

    Returns:
        dict: Dictionary containing 'title', 'author', and 'fsds_number'
    """
    # Initialize Jira connection
    jira = init_jira_connection()

    # Get issue from Jira
    issue = get_jira_issue(jira, fsds_number)

    # Extract title and reporter
    title, author = get_title_reporter_from_issue(issue)

    return {
        'title': title,
        'author': author,
        'fsds_number': fsds_number
    }


def generate_review_email_html(ticket_info, template_file='email-template.md'):
    """
    Generate HTML review email from template and ticket info.

    Args:
        ticket_info (dict): Dictionary with title, author, fsds_number, review_deadline, signature
        template_file (str): Path to email template file

    Returns:
        str: HTML formatted email content
    """
    import html

    # Prepare template variables from ticket_info
    template_vars = {
        'author': ticket_info['author'],
        'title': ticket_info['title'],
        'fsds_number': f"FSDS-{ticket_info['fsds_number']}",
        'review_deadline': ticket_info['review_deadline'],
        'signature': ticket_info['signature']
    }

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)

    # Render template
    email_text = template.render(template_vars)

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


def calculate_review_deadline():
    """
    Calculate review deadline as 3 weekdays from today.

    Returns:
        str: Formatted deadline string like "Wednesday January 14"
    """
    from datetime import datetime, timedelta

    today = datetime.now()
    weekdays_added = 0
    current_date = today

    while weekdays_added < 3:
        current_date += timedelta(days=1)
        # Monday=0, Sunday=6, so weekdays are 0-4
        if current_date.weekday() < 5:
            weekdays_added += 1

    return current_date.strftime("%A %B %d").replace(" 0", " ")


def get_user_first_name():
    """
    Get user's first name from git config.

    Returns:
        str: First name from git config or "User" as fallback
    """
    try:
        git_name = subprocess.run(['git', 'config', '--get', 'user.name'],
                                 capture_output=True, text=True, check=True)
        full_name = git_name.stdout.strip()
        first_name = full_name.split()[0] if full_name else "User"
    except (subprocess.CalledProcessError, IndexError):
        first_name = "User"
    return first_name


def main():
    """Main function with argparse CLI."""
    parser = argparse.ArgumentParser(
        description='Get ticket information from Jira API and generate review email'
    )
    parser.add_argument(
        'fsds_number',
        type=int,
        help='FSDS ticket number (e.g., 189 for FSDS-189)'
    )
    parser.add_argument(
        '--open',
        action='store_true',
        help='Automatically open the generated HTML file in browser'
    )

    args = parser.parse_args()

    try:
        info = get_ticket_info_from_jira(args.fsds_number)

        # Add computed fields to ticket info
        info['review_deadline'] = calculate_review_deadline()
        info['signature'] = get_user_first_name()

        # Always show parsed information
        print(f"FSDS Number: {info['fsds_number']}")
        print(f"Title: {info['title']}")
        print(f"Author: {info['author']}")

        # Write info dict to JSON file
        info_file = f"FSDS-{info['fsds_number']}-info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2)
        print(f"Ticket info written to: {info_file}")

        # Generate HTML email
        html_email = generate_review_email_html(info)
        output_file = f"FSDS-{info['fsds_number']}-review-email.html"
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