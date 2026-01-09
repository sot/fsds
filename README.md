# FSDS Review Email Generator

A Python tool to retrieve ticket information from Jira API and automatically generate review announcement and approved emails for Flight Support Data Systems (FSDS) change requests.

## Features

- Retrieves ticket information directly from Jira API:
  - FSDS ticket number
  - Ticket title
  - Reporter/author name
  - Review deadline (3 weekdays from current date)
  - User signature from git config
- Generates HTML-formatted review announcement emails
- Generates plain text approved emails
- Preserves email template formatting with proper indentation
- Optional automatic browser opening of generated HTML
- Saves ticket information to JSON for reuse

## Scripts

### `write_review_email.py`
Main script for retrieving ticket info from Jira API and generating review announcement emails.

### `write_approved_email.py`
Script for generating approved emails from previously saved ticket JSON data.

## Usage

### Prerequisites

1. You need a Jira API token stored in `~/jira_api_token.txt`
2. The token should have read access to the FSDS project in Jira

### Review Email Generation

#### Basic usage with FSDS number:
```bash
python write_review_email.py 189
```

#### Automatically open generated HTML in browser:
```bash
python write_review_email.py 189 --open
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
- Jinja2
- jira (Python Jira API library)

Install dependencies:
```bash
pip install jinja2 jira
```

## Setup

1. Create a Jira API token:
   - Go to your Jira profile settings
   - Generate an API token
   - Save the token to `~/jira_api_token.txt`

2. Ensure your token has read access to the FSDS project

## Files

- `write_review_email.py` - Main script for review email generation (uses Jira API)
- `write_approved_email.py` - Script for approved email generation
- `email-template.md` - Jinja2 template for review announcement emails
- `approved-template.md` - Jinja2 template for approved emails

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
1. Console output showing retrieved ticket information
2. HTML file named `FSDS-{number}-review-email.html` with formatted review announcement
3. JSON file named `FSDS-{number}-info.json` with ticket data for later use

### Approved Email Script
The script generates:
1. Plain text output ready to copy/paste into email
2. Console display of approved email content

## License

BSD 3-Clause License. See LICENSE file for details.

## Copyright

Copyright (c) 2026, Smithsonian Astrophysical Observatory