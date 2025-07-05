#!/usr/bin/env python3
"""
JIRA Ticket Validator

This script validates various aspects of JIRA tickets including:
- Date time fields (creation date, due date, updated date)
- Status values
- Attachments (existence, file types, sizes)
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import requests
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JiraTicketValidator:
    """A comprehensive validator for JIRA tickets"""
    
    def __init__(self, jira_url: str, username: str, password: str):
        """
        Initialize the JIRA validator
        
        Args:
            jira_url: JIRA server URL (e.g., https://your-company.atlassian.net)
            username: JIRA username or email
            password: JIRA password or API token
        """
        self.jira_url = jira_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        
        # Valid status categories
        self.valid_status_categories = [
            'new', 'indeterminate', 'done', 'to do', 'in progress'
        ]
        
        # Valid attachment file types (configurable)
        self.allowed_file_types = [
            '.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', 
            '.gif', '.xlsx', '.xls', '.csv', '.zip', '.rar', '.log'
        ]
        
        # Maximum attachment size in bytes (50MB by default)
        self.max_attachment_size = 50 * 1024 * 1024

    def get_ticket(self, ticket_key: str) -> Optional[Dict]:
        """
        Retrieve ticket information from JIRA
        
        Args:
            ticket_key: JIRA ticket key (e.g., 'PROJECT-123')
            
        Returns:
            Dictionary containing ticket data or None if not found
        """
        try:
            url = f"{self.jira_url}/rest/api/2/issue/{ticket_key}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving ticket {ticket_key}: {e}")
            return None

    def validate_datetime_fields(self, ticket_data: Dict) -> List[str]:
        """
        Validate date time fields in the ticket
        
        Args:
            ticket_data: JIRA ticket data dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        fields = ticket_data.get('fields', {})
        
        # Check creation date
        created = fields.get('created')
        if created:
            try:
                created_date = datetime.strptime(created[:19], '%Y-%m-%dT%H:%M:%S')
                if created_date > datetime.now():
                    errors.append("Creation date cannot be in the future")
            except ValueError:
                errors.append("Invalid creation date format")
        else:
            errors.append("Creation date is missing")
        
        # Check updated date
        updated = fields.get('updated')
        if updated:
            try:
                updated_date = datetime.strptime(updated[:19], '%Y-%m-%dT%H:%M:%S')
                if updated_date > datetime.now():
                    errors.append("Updated date cannot be in the future")
                    
                # Updated date should be after creation date
                if created:
                    created_date = datetime.strptime(created[:19], '%Y-%m-%dT%H:%M:%S')
                    if updated_date < created_date:
                        errors.append("Updated date cannot be before creation date")
            except ValueError:
                errors.append("Invalid updated date format")
        
        # Check due date
        duedate = fields.get('duedate')
        if duedate:
            try:
                due_date = datetime.strptime(duedate, '%Y-%m-%d')
                if due_date.date() < datetime.now().date():
                    errors.append("Due date is in the past")
            except ValueError:
                errors.append("Invalid due date format")
        
        # Check resolution date
        resolutiondate = fields.get('resolutiondate')
        if resolutiondate:
            try:
                resolution_date = datetime.strptime(resolutiondate[:19], '%Y-%m-%dT%H:%M:%S')
                if resolution_date > datetime.now():
                    errors.append("Resolution date cannot be in the future")
            except ValueError:
                errors.append("Invalid resolution date format")
        
        return errors

    def validate_status(self, ticket_data: Dict) -> List[str]:
        """
        Validate ticket status
        
        Args:
            ticket_data: JIRA ticket data dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        fields = ticket_data.get('fields', {})
        status = fields.get('status', {})
        
        if not status:
            errors.append("Status is missing")
            return errors
        
        status_name = status.get('name', '').lower()
        status_category = status.get('statusCategory', {}).get('name', '').lower()
        
        # Check if status name exists
        if not status_name:
            errors.append("Status name is missing")
        
        # Check if status category is valid
        if status_category and status_category not in self.valid_status_categories:
            errors.append(f"Invalid status category: {status_category}")
        
        # Check for logical status transitions
        resolution = fields.get('resolution')
        if status_category == 'done' and not resolution:
            errors.append("Resolved/Done tickets should have a resolution")
        
        if status_category != 'done' and resolution:
            errors.append("Only resolved/done tickets should have a resolution")
        
        return errors

    def validate_attachments(self, ticket_data: Dict) -> List[str]:
        """
        Validate ticket attachments
        
        Args:
            ticket_data: JIRA ticket data dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        fields = ticket_data.get('fields', {})
        attachment = fields.get('attachment', [])
        
        if not attachment:
            # This might not be an error depending on requirements
            logger.info("No attachments found in ticket")
            return errors
        
        for idx, att in enumerate(attachment):
            att_errors = []
            
            # Check filename
            filename = att.get('filename', '')
            if not filename:
                att_errors.append(f"Attachment {idx + 1}: Missing filename")
            else:
                # Check file extension
                file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
                if file_ext not in self.allowed_file_types:
                    att_errors.append(f"Attachment {idx + 1}: Invalid file type '{file_ext}'")
            
            # Check file size
            size = att.get('size', 0)
            if size > self.max_attachment_size:
                size_mb = size / (1024 * 1024)
                max_size_mb = self.max_attachment_size / (1024 * 1024)
                att_errors.append(f"Attachment {idx + 1}: File size ({size_mb:.2f}MB) exceeds maximum ({max_size_mb}MB)")
            
            # Check creation date
            created = att.get('created')
            if created:
                try:
                    att_created = datetime.strptime(created[:19], '%Y-%m-%dT%H:%M:%S')
                    if att_created > datetime.now():
                        att_errors.append(f"Attachment {idx + 1}: Creation date cannot be in the future")
                except ValueError:
                    att_errors.append(f"Attachment {idx + 1}: Invalid creation date format")
            
            # Check if attachment author exists
            author = att.get('author', {})
            if not author.get('name'):
                att_errors.append(f"Attachment {idx + 1}: Missing author information")
            
            errors.extend(att_errors)
        
        return errors

    def validate_ticket(self, ticket_key: str) -> Dict[str, Any]:
        """
        Perform comprehensive validation of a JIRA ticket
        
        Args:
            ticket_key: JIRA ticket key (e.g., 'PROJECT-123')
            
        Returns:
            Dictionary containing validation results
        """
        logger.info(f"Validating ticket: {ticket_key}")
        
        result = {
            'ticket_key': ticket_key,
            'is_valid': True,
            'errors': {
                'datetime': [],
                'status': [],
                'attachments': [],
                'general': []
            },
            'warnings': [],
            'ticket_data': None
        }
        
        # Get ticket data
        ticket_data = self.get_ticket(ticket_key)
        if not ticket_data:
            result['is_valid'] = False
            result['errors']['general'].append("Unable to retrieve ticket data")
            return result
        
        result['ticket_data'] = ticket_data
        
        # Validate datetime fields
        datetime_errors = self.validate_datetime_fields(ticket_data)
        result['errors']['datetime'] = datetime_errors
        
        # Validate status
        status_errors = self.validate_status(ticket_data)
        result['errors']['status'] = status_errors
        
        # Validate attachments
        attachment_errors = self.validate_attachments(ticket_data)
        result['errors']['attachments'] = attachment_errors
        
        # Check if any errors found
        total_errors = len(datetime_errors) + len(status_errors) + len(attachment_errors)
        if total_errors > 0:
            result['is_valid'] = False
        
        return result

    def validate_multiple_tickets(self, ticket_keys: List[str]) -> Dict[str, Any]:
        """
        Validate multiple tickets at once
        
        Args:
            ticket_keys: List of JIRA ticket keys
            
        Returns:
            Dictionary containing validation results for all tickets
        """
        results = {
            'total_tickets': len(ticket_keys),
            'valid_tickets': 0,
            'invalid_tickets': 0,
            'results': {}
        }
        
        for ticket_key in ticket_keys:
            ticket_result = self.validate_ticket(ticket_key)
            results['results'][ticket_key] = ticket_result
            
            if ticket_result['is_valid']:
                results['valid_tickets'] += 1
            else:
                results['invalid_tickets'] += 1
        
        return results

    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """
        Generate a human-readable validation report
        
        Args:
            validation_results: Results from validate_ticket or validate_multiple_tickets
            
        Returns:
            Formatted report string
        """
        if 'total_tickets' in validation_results:
            # Multiple tickets report
            report = f"JIRA Ticket Validation Report\n"
            report += f"{'=' * 40}\n\n"
            report += f"Total Tickets: {validation_results['total_tickets']}\n"
            report += f"Valid Tickets: {validation_results['valid_tickets']}\n"
            report += f"Invalid Tickets: {validation_results['invalid_tickets']}\n\n"
            
            for ticket_key, result in validation_results['results'].items():
                report += f"Ticket: {ticket_key}\n"
                report += f"Status: {'✓ VALID' if result['is_valid'] else '✗ INVALID'}\n"
                
                if not result['is_valid']:
                    for category, errors in result['errors'].items():
                        if errors:
                            report += f"  {category.upper()} Errors:\n"
                            for error in errors:
                                report += f"    - {error}\n"
                report += "\n"
        else:
            # Single ticket report
            report = f"JIRA Ticket Validation Report\n"
            report += f"{'=' * 40}\n\n"
            report += f"Ticket: {validation_results['ticket_key']}\n"
            report += f"Status: {'✓ VALID' if validation_results['is_valid'] else '✗ INVALID'}\n\n"
            
            if not validation_results['is_valid']:
                for category, errors in validation_results['errors'].items():
                    if errors:
                        report += f"{category.upper()} Errors:\n"
                        for error in errors:
                            report += f"  - {error}\n"
                        report += "\n"
        
        return report


def main():
    """
    Example usage of the JIRA Ticket Validator
    """
    # Configuration
    JIRA_URL = "https://your-company.atlassian.net"
    USERNAME = "your-email@company.com"
    PASSWORD = "your-api-token"  # Use API token instead of password
    
    # Initialize validator
    validator = JiraTicketValidator(JIRA_URL, USERNAME, PASSWORD)
    
    # Example 1: Validate a single ticket
    ticket_key = "PROJECT-123"
    result = validator.validate_ticket(ticket_key)
    print(validator.generate_validation_report(result))
    
    # Example 2: Validate multiple tickets
    ticket_keys = ["PROJECT-123", "PROJECT-124", "PROJECT-125"]
    results = validator.validate_multiple_tickets(ticket_keys)
    print(validator.generate_validation_report(results))


if __name__ == "__main__":
    main()