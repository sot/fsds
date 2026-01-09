#!/usr/bin/env python3
"""
Script to extract ticket information from Jira HTML files.
"""

import re
from bs4 import BeautifulSoup


def extract_ticket_info(html_file_path):
    """
    Extract ticket information from a Jira HTML file.
    
    Args:
        html_file_path (str): Path to the Jira HTML file
        
    Returns:
        dict: Dictionary containing 'title', 'author', and 'fsds_number'
    """
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
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
        if len(words) >= 2 and all(word[0].isupper() for word in words[:2]):
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


def main():
    """Main function to demonstrate usage."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python write_review_email.py <jira_html_file>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    try:
        info = extract_ticket_info(html_file)
        print(f"FSDS Number: {info['fsds_number']}")
        print(f"Title: {info['title']}")
        print(f"Author: {info['author']}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()