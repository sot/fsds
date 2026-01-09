# FSDS Review Email Generator

A Python tool to extract ticket information from Jira HTML files and automatically generate review announcement and approved emails for Flight Support Data Systems (FSDS) change requests.

## Features

- Extracts ticket information from Jira HTML export files:
  - FSDS ticket number
  - Ticket title
  - Reporter/author name
  - Review deadline (3 weekdays from current date)
  - User signature from git config
- Generates HTML-formatted review announcement emails
- Generates plain text approved emails
- Preserves email template formatting with proper indentation
- Supports both file input and clipboard input (Mac)
- Optional automatic browser opening of generated HTML
- Saves ticket information to JSON for reuse

## Scripts

### `write_review_email.py`
Main script for extracting ticket info and generating review announcement emails.

### `write_approved_email.py`
Script for generating approved emails from previously saved ticket JSON data.

## Usage

### Getting Jira HTML (Mac instructions)

1. Go to the FSDS Jira ticket page in your browser
2. View the page source (⌘+Option+U or right-click → "View Page Source")
3. Select all content (⌘+A) and copy (⌘+C)
4. The HTML is now in your clipboard ready to use with `pbpaste`

### Review Email Generation

#### Basic usage with file input:
```bash
python write_review_email.py jira-ticket.html
```

#### Reading from clipboard (Mac):
```bash
pbpaste | python write_review_email.py
```

*Note: `pbpaste` is a Mac utility that outputs clipboard contents to stdout*

#### Automatically open generated HTML in browser:
```bash
python write_review_email.py jira-ticket.html --open
```

### Approved Email Generation

After generating a review email, you can create an approved email:

```bash
python write_approved_email.py 189
```

This reads the saved JSON file (`FSDS-189-info.json`) and generates approved email text.

### Get help:
```bash
python write_review_email.py --help
python write_approved_email.py --help
```

## Requirements

- Python 3.6+
- BeautifulSoup4
- Jinja2

Install dependencies:
```bash
pip install beautifulsoup4 jinja2
```

## Files

- `write_review_email.py` - Main script for review email generation
- `write_approved_email.py` - Script for approved email generation
- `email-template.md` - Jinja2 template for review announcement emails
- `approved-template.md` - Jinja2 template for approved emails
- `jira-fsds-ticket.html` - Example Jira HTML export file

## Template Variables

The email templates support the following placeholders:

### Review Email Template (email-template.md)
- `{{author}}` - Ticket reporter/author name
- `{{fsds_number}}` - Full FSDS ticket identifier (e.g., "FSDS-189")
- `{{title}}` - Ticket title/summary
- `{{review_deadline}}` - Automatically calculated review deadline (3 weekdays from today)
- `{{signature}}` - User's first name from git config

### Approved Email Template (approved-template.md)
- `{{author}}` - Ticket reporter/author name
- `{{fsds_number}}` - Full FSDS ticket identifier (e.g., "FSDS-189")
- `{{title}}` - Ticket title/summary
- `{{signature}}` - User's first name from git config

## Output

### Review Email Script
The script generates:
1. Console output showing parsed ticket information
2. HTML file named `review_email_FSDS-{number}.html` with formatted review announcement
3. JSON file named `FSDS-{number}-info.json` with ticket data for later use

### Approved Email Script
The script generates:
1. Plain text output ready to copy/paste into email
2. Console display of approved email content

## License

BSD 3-Clause License. See LICENSE file for details.

## Copyright

Copyright (c) 2026, Smithsonian Astrophysical Observatory