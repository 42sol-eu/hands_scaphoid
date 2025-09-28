#!/usr/bin/env python3
"""
Usage examples for the import_organizer.py script.

This file demonstrates various ways to use the import organizer script
to clean up and organize Python imports according to the project standards.
"""

# Example usage commands:

# 1. Basic usage - organize imports in a single file
# python import_organizer.py my_file.py

# 2. Dry run - see what changes would be made without modifying files
# python import_organizer.py --dry-run my_file.py

# 3. Create backup before modifying
# python import_organizer.py --backup my_file.py

# 4. Process multiple files
# python import_organizer.py file1.py file2.py file3.py

# 5. Process all Python files in a directory (PowerShell)
# python import_organizer.py src/**/*.py

# 6. Verbose output for detailed information
# python import_organizer.py --verbose --dry-run src/hands_scaphoid/**/*.py

# 7. Remove unused imports (experimental)
# python import_organizer.py --remove-unused --backup my_file.py

def example_usage():
    """Show example command lines for different scenarios."""
    examples = [
        {
            "description": "Organize imports in current project files",
            "command": "python import_organizer.py src/hands_scaphoid/**/*.py",
        },
        {
            "description": "Preview changes without modifying files",
            "command": "python import_organizer.py --dry-run --verbose src/hands_scaphoid/commands/*.py",
        },
        {
            "description": "Safe modification with backups",
            "command": "python import_organizer.py --backup --verbose src/hands_scaphoid/contexts/*.py",
        },
        {
            "description": "Process a single file with detailed output",
            "command": "python import_organizer.py --verbose my_messy_file.py",
        },
    ]
    
    print("Import Organizer Usage Examples:")
    print("=" * 50)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   {example['command']}")
    
    print("\nThe script will:")
    print("• Organize imports into #%% [section] format")
    print("• Sort imports alphabetically")
    print("• Group 'from X import' statements with proper formatting")
    print("• Detect unused imports (reported but not removed by default)")
    print("• Categorize imports as Standard library, Third party, or Local")

if __name__ == '__main__':
    example_usage()