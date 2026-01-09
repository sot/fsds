# FSDS Review Email Generator

A Python tool to extract ticket information from Jira HTML files and automatically generate review announcement emails for Flight Support Data Systems (FSDS) change requests.

## Features

- Extracts ticket information from Jira HTML export files:
  - FSDS ticket number
  - Ticket title
  - Reporter/author name
- Generates HTML-formatted review announcement emails
- Automatically calculates review deadline (3 weekdays from current date)
- Preserves email template formatting with proper indentation
- Supports both file input and STDIN input
- Optional automatic browser opening of generated HTML

## Usage

### Basic usage with file input:
```bash
python write_review_email.py jira-ticket.html
```

### Reading from STDIN (useful for piped input):
```bash
cat jira-ticket.html | python write_review_email.py
```

### Automatically open generated HTML in browser:
```bash
python write_review_email.py jira-ticket.html --open
```

### Get help:
```bash
python write_review_email.py --help
```

## Requirements

- Python 3.6+
- BeautifulSoup4: `pip install beautifulsoup4`

## Files

- `write_review_email.py` - Main script for extracting ticket info and generating emails
- `email-template.md` - Markdown template for review announcement emails
- `jira-fsds-ticket.html` - Example Jira HTML export file

## Template Variables

The email template supports the following placeholders:

- `{{author}}` - Ticket reporter/author name
- `{{fsds_number}}` - Full FSDS ticket identifier (e.g., "FSDS-189")
- `{{title}}` - Ticket title/summary
- `{{review_deadline}}` - Automatically calculated review deadline (3 weekdays from today)

## Output

The script generates:
1. Console output showing parsed ticket information
2. HTML file named `review_email_FSDS-{number}.html` with formatted review announcement

## License

BSD 3-Clause License. See LICENSE file for details.

## Copyright

Copyright (c) 2026, Smithsonian Astrophysical Observatory