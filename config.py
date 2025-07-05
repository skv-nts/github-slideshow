"""
Configuration file for JIRA Ticket Validator
Copy this file and customize it for your environment
"""

# JIRA Connection Settings
JIRA_URL = "https://your-company.atlassian.net"
USERNAME = "your-email@company.com"
PASSWORD = "your-api-token"  # Use API token instead of password

# Validation Settings
VALID_STATUS_CATEGORIES = [
    'new', 'indeterminate', 'done', 'to do', 'in progress'
]

# Allowed file types for attachments
ALLOWED_FILE_TYPES = [
    '.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png',
    '.gif', '.xlsx', '.xls', '.csv', '.zip', '.rar', '.log'
]

# Maximum attachment size in bytes (50MB by default)
MAX_ATTACHMENT_SIZE = 50 * 1024 * 1024

# Custom validation rules (optional)
CUSTOM_RULES = {
    'require_due_date': False,  # Set to True if all tickets must have a due date
    'require_attachments': False,  # Set to True if all tickets must have attachments
    'max_age_days': 365,  # Maximum age in days for tickets
    'required_fields': [],  # List of custom fields that must be present
}

# Logging configuration
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'jira_validator.log'  # Set to None to disable file logging