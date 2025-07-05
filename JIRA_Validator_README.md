# JIRA Ticket Validator

A comprehensive Python tool for validating JIRA tickets, including date/time fields, status, and attachments.

## Features

- **Date/Time Validation**: Validates creation dates, due dates, updated dates, and resolution dates
- **Status Validation**: Checks ticket status and status categories
- **Attachment Validation**: Validates file types, sizes, and attachment metadata
- **Batch Processing**: Validate multiple tickets at once
- **Comprehensive Reporting**: Generate detailed validation reports
- **Configurable Rules**: Customize validation rules for your environment

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your JIRA connection in `config.py`:
```python
JIRA_URL = "https://your-company.atlassian.net"
USERNAME = "your-email@company.com"
PASSWORD = "your-api-token"  # Use API token instead of password
```

## Quick Start

### Basic Usage

```python
from jira_ticket_validator import JiraTicketValidator
import config

# Initialize validator
validator = JiraTicketValidator(config.JIRA_URL, config.USERNAME, config.PASSWORD)

# Validate a single ticket
result = validator.validate_ticket("PROJECT-123")

# Print validation report
print(validator.generate_validation_report(result))
```

### Validate Multiple Tickets

```python
ticket_keys = ["PROJECT-123", "PROJECT-124", "PROJECT-125"]
results = validator.validate_multiple_tickets(ticket_keys)
print(validator.generate_validation_report(results))
```

## Validation Categories

### 1. Date/Time Validation

The validator checks the following date/time fields:

- **Creation Date**: Must not be in the future
- **Updated Date**: Must not be in the future, must be after creation date
- **Due Date**: Warns if in the past
- **Resolution Date**: Must not be in the future (for resolved tickets)

### 2. Status Validation

- Validates status categories against predefined valid categories
- Checks logical consistency (resolved tickets should have resolution)
- Ensures status name is present

### 3. Attachment Validation

- **File Types**: Validates against allowed file extensions
- **File Size**: Checks against maximum size limits
- **Metadata**: Validates attachment creation date and author information

## Configuration

### Basic Configuration

Edit `config.py` to customize validation settings:

```python
# Allowed file types for attachments
ALLOWED_FILE_TYPES = [
    '.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png',
    '.gif', '.xlsx', '.xls', '.csv', '.zip', '.rar', '.log'
]

# Maximum attachment size in bytes (50MB by default)
MAX_ATTACHMENT_SIZE = 50 * 1024 * 1024

# Valid status categories
VALID_STATUS_CATEGORIES = [
    'new', 'indeterminate', 'done', 'to do', 'in progress'
]
```

### Runtime Configuration

You can also customize validation settings at runtime:

```python
validator = JiraTicketValidator(jira_url, username, password)

# Customize file types
validator.allowed_file_types = ['.pdf', '.doc', '.docx']

# Set size limit (10MB)
validator.max_attachment_size = 10 * 1024 * 1024

# Add custom status categories
validator.valid_status_categories.extend(['custom status', 'review'])
```

## API Reference

### JiraTicketValidator Class

#### Constructor
```python
JiraTicketValidator(jira_url: str, username: str, password: str)
```

#### Methods

##### `validate_ticket(ticket_key: str) -> Dict[str, Any]`
Validates a single JIRA ticket.

**Parameters:**
- `ticket_key`: JIRA ticket key (e.g., 'PROJECT-123')

**Returns:**
```python
{
    'ticket_key': str,
    'is_valid': bool,
    'errors': {
        'datetime': List[str],
        'status': List[str],
        'attachments': List[str],
        'general': List[str]
    },
    'warnings': List[str],
    'ticket_data': Dict  # Raw JIRA ticket data
}
```

##### `validate_multiple_tickets(ticket_keys: List[str]) -> Dict[str, Any]`
Validates multiple JIRA tickets.

**Parameters:**
- `ticket_keys`: List of JIRA ticket keys

**Returns:**
```python
{
    'total_tickets': int,
    'valid_tickets': int,
    'invalid_tickets': int,
    'results': Dict[str, Any]  # Individual ticket results
}
```

##### `generate_validation_report(validation_results: Dict[str, Any]) -> str`
Generates a human-readable validation report.

## Examples

### Example 1: Single Ticket Validation

```python
from jira_ticket_validator import JiraTicketValidator
import config

validator = JiraTicketValidator(config.JIRA_URL, config.USERNAME, config.PASSWORD)
result = validator.validate_ticket("PROJECT-123")

if result['is_valid']:
    print("✓ Ticket is valid!")
else:
    print("✗ Validation errors found:")
    for category, errors in result['errors'].items():
        if errors:
            print(f"  {category.upper()}:")
            for error in errors:
                print(f"    - {error}")
```

### Example 2: Batch Validation from File

```python
# Read ticket keys from file
with open("tickets.txt", "r") as f:
    ticket_keys = [line.strip() for line in f if line.strip()]

# Validate all tickets
validator = JiraTicketValidator(config.JIRA_URL, config.USERNAME, config.PASSWORD)
results = validator.validate_multiple_tickets(ticket_keys)

# Save report to file
with open("validation_report.txt", "w") as f:
    f.write(validator.generate_validation_report(results))
```

### Example 3: Custom Validation Rules

```python
validator = JiraTicketValidator(config.JIRA_URL, config.USERNAME, config.PASSWORD)

# Only allow PDF and Word documents
validator.allowed_file_types = ['.pdf', '.doc', '.docx']

# Set 10MB size limit
validator.max_attachment_size = 10 * 1024 * 1024

# Add custom status
validator.valid_status_categories.append('under review')

result = validator.validate_ticket("PROJECT-123")
```

## Error Handling

The validator includes comprehensive error handling:

```python
try:
    validator = JiraTicketValidator(jira_url, username, password)
    result = validator.validate_ticket("PROJECT-123")
except requests.exceptions.ConnectionError:
    print("Unable to connect to JIRA server")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## JIRA API Token Setup

For security, use API tokens instead of passwords:

1. Log in to your Atlassian account
2. Go to Security → API tokens
3. Create a new API token
4. Use your email address as the username and the token as the password

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your JIRA URL is correct
   - Ensure you're using an API token, not a password
   - Check that your account has permission to access the tickets

2. **Connection Errors**
   - Verify network connectivity to JIRA server
   - Check if you're behind a corporate firewall
   - Ensure JIRA URL includes the correct protocol (https://)

3. **Permission Errors**
   - Verify your account has permission to read tickets
   - Check if the ticket exists and you have access to it
   - Ensure you have permission to view attachments

### Debugging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

validator = JiraTicketValidator(jira_url, username, password)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the examples
3. Open an issue on GitHub

---

## File Structure

```
jira_ticket_validator/
├── jira_ticket_validator.py  # Main validator class
├── config.py                 # Configuration settings
├── example_usage.py          # Usage examples
├── requirements.txt          # Python dependencies
└── README.md                # This file
```