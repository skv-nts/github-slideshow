#!/usr/bin/env python3
"""
Example usage of the JIRA Ticket Validator
This file demonstrates various ways to use the validator
"""

from jira_ticket_validator import JiraTicketValidator
import config

def example_single_ticket_validation():
    """Example: Validate a single ticket"""
    print("Example 1: Single Ticket Validation")
    print("-" * 40)
    
    # Initialize validator
    validator = JiraTicketValidator(
        config.JIRA_URL, 
        config.USERNAME, 
        config.PASSWORD
    )
    
    # Validate a single ticket
    ticket_key = "PROJECT-123"
    result = validator.validate_ticket(ticket_key)
    
    # Print the validation report
    print(validator.generate_validation_report(result))
    
    # Access specific validation results
    if result['is_valid']:
        print("✓ Ticket passed all validations!")
    else:
        print("✗ Ticket failed validation:")
        for category, errors in result['errors'].items():
            if errors:
                print(f"  {category.upper()} issues:")
                for error in errors:
                    print(f"    - {error}")

def example_multiple_tickets_validation():
    """Example: Validate multiple tickets"""
    print("\nExample 2: Multiple Tickets Validation")
    print("-" * 40)
    
    validator = JiraTicketValidator(
        config.JIRA_URL, 
        config.USERNAME, 
        config.PASSWORD
    )
    
    # List of tickets to validate
    ticket_keys = ["PROJECT-123", "PROJECT-124", "PROJECT-125"]
    
    # Validate all tickets
    results = validator.validate_multiple_tickets(ticket_keys)
    
    # Print summary
    print(f"Validation Summary:")
    print(f"Total tickets: {results['total_tickets']}")
    print(f"Valid tickets: {results['valid_tickets']}")
    print(f"Invalid tickets: {results['invalid_tickets']}")
    
    # Print detailed report
    print("\nDetailed Report:")
    print(validator.generate_validation_report(results))

def example_custom_validator():
    """Example: Custom validator with modified settings"""
    print("\nExample 3: Custom Validator Settings")
    print("-" * 40)
    
    validator = JiraTicketValidator(
        config.JIRA_URL, 
        config.USERNAME, 
        config.PASSWORD
    )
    
    # Customize validation settings
    validator.allowed_file_types = ['.pdf', '.doc', '.docx']  # Only allow documents
    validator.max_attachment_size = 10 * 1024 * 1024  # 10MB limit
    
    # Add custom status categories
    validator.valid_status_categories.extend(['custom status', 'review'])
    
    # Validate with custom settings
    ticket_key = "PROJECT-123"
    result = validator.validate_ticket(ticket_key)
    print(validator.generate_validation_report(result))

def example_error_handling():
    """Example: Error handling for common issues"""
    print("\nExample 4: Error Handling")
    print("-" * 40)
    
    validator = JiraTicketValidator(
        config.JIRA_URL, 
        config.USERNAME, 
        config.PASSWORD
    )
    
    # Try to validate a non-existent ticket
    result = validator.validate_ticket("NONEXISTENT-999")
    
    if not result['is_valid']:
        print("Expected error for non-existent ticket:")
        print(f"Errors: {result['errors']['general']}")
    
    # Example of handling network errors
    try:
        # This would handle cases where JIRA is unreachable
        result = validator.validate_ticket("PROJECT-123")
    except Exception as e:
        print(f"Network or authentication error: {e}")

def example_batch_validation_from_file():
    """Example: Validate tickets from a file"""
    print("\nExample 5: Batch Validation from File")
    print("-" * 40)
    
    # Create a sample file with ticket keys
    ticket_keys = ["PROJECT-123", "PROJECT-124", "PROJECT-125"]
    
    with open("tickets_to_validate.txt", "w") as f:
        for ticket in ticket_keys:
            f.write(f"{ticket}\n")
    
    # Read tickets from file and validate
    validator = JiraTicketValidator(
        config.JIRA_URL, 
        config.USERNAME, 
        config.PASSWORD
    )
    
    with open("tickets_to_validate.txt", "r") as f:
        tickets = [line.strip() for line in f.readlines() if line.strip()]
    
    results = validator.validate_multiple_tickets(tickets)
    
    # Save results to file
    with open("validation_results.txt", "w") as f:
        f.write(validator.generate_validation_report(results))
    
    print("Validation completed. Results saved to validation_results.txt")

def example_validation_with_filtering():
    """Example: Validate tickets with specific criteria"""
    print("\nExample 6: Validation with Filtering")
    print("-" * 40)
    
    validator = JiraTicketValidator(
        config.JIRA_URL, 
        config.USERNAME, 
        config.PASSWORD
    )
    
    ticket_key = "PROJECT-123"
    result = validator.validate_ticket(ticket_key)
    
    # Filter results to show only specific types of errors
    datetime_errors = result['errors']['datetime']
    attachment_errors = result['errors']['attachments']
    
    if datetime_errors:
        print("Date/Time Issues Found:")
        for error in datetime_errors:
            print(f"  - {error}")
    
    if attachment_errors:
        print("Attachment Issues Found:")
        for error in attachment_errors:
            print(f"  - {error}")
    
    if not datetime_errors and not attachment_errors:
        print("No date/time or attachment issues found!")

if __name__ == "__main__":
    print("JIRA Ticket Validator - Usage Examples")
    print("=" * 50)
    
    # Run all examples
    try:
        example_single_ticket_validation()
        example_multiple_tickets_validation()
        example_custom_validator()
        example_error_handling()
        example_batch_validation_from_file()
        example_validation_with_filtering()
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Please check your configuration in config.py")