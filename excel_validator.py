import pandas as pd
import numpy as np
from tabulate import tabulate
import re

class ExcelValidator:
    def __init__(self):
        self.validation_results = []
        self.df = None

    def load_excel(self, file_path):
        """Load the Excel file into a pandas DataFrame"""
        try:
            self.df = pd.read_excel(file_path)
            print(f"Successfully loaded Excel file with {len(self.df)} rows")
            return True
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return False

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, str(email)))

    def validate_phone(self, phone):
        """Validate phone number format"""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, str(phone)))

    def validate_data(self, rules):
        """Validate data based on specified rules"""
        self.validation_results = []
        
        for index, row in self.df.iterrows():
            row_number = index + 2  # Adding 2 because Excel rows start at 1 and header is row 1
            
            for column, rule in rules.items():
                if column not in self.df.columns:
                    self.validation_results.append({
                        'Row': row_number,
                        'Column': column,
                        'Value': 'N/A',
                        'Error': 'Column not found in Excel file'
                    })
                    continue

                value = row[column]
                
                # Check if required
                if rule.get('required', False) and pd.isna(value):
                    self.validation_results.append({
                        'Row': row_number,
                        'Column': column,
                        'Value': value,
                        'Error': 'Required field is empty'
                    })
                    continue

                # Skip further validation if value is empty and not required
                if pd.isna(value):
                    continue

                # Type validation
                if 'type' in rule:
                    if rule['type'] == 'email' and not self.validate_email(value):
                        self.validation_results.append({
                            'Row': row_number,
                            'Column': column,
                            'Value': value,
                            'Error': 'Invalid email format'
                        })
                    elif rule['type'] == 'phone' and not self.validate_phone(value):
                        self.validation_results.append({
                            'Row': row_number,
                            'Column': column,
                            'Value': value,
                            'Error': 'Invalid phone number format'
                        })
                    elif rule['type'] == 'numeric' and not str(value).replace('.', '').isdigit():
                        self.validation_results.append({
                            'Row': row_number,
                            'Column': column,
                            'Value': value,
                            'Error': 'Not a valid number'
                        })

                # Range validation
                if 'min' in rule and float(value) < rule['min']:
                    self.validation_results.append({
                        'Row': row_number,
                        'Column': column,
                        'Value': value,
                        'Error': f'Value below minimum ({rule["min"]})'
                    })
                if 'max' in rule and float(value) > rule['max']:
                    self.validation_results.append({
                        'Row': row_number,
                        'Column': column,
                        'Value': value,
                        'Error': f'Value above maximum ({rule["max"]})'
                    })

                # List validation
                if 'allowed_values' in rule and value not in rule['allowed_values']:
                    self.validation_results.append({
                        'Row': row_number,
                        'Column': column,
                        'Value': value,
                        'Error': f'Value not in allowed list: {rule["allowed_values"]}'
                    })

    def display_results(self):
        """Display validation results in a table format"""
        if not self.validation_results:
            print("\nNo validation errors found! ✅")
            return

        print("\nValidation Errors Found:")
        print(tabulate(self.validation_results, headers='keys', tablefmt='grid'))
        print(f"\nTotal errors found: {len(self.validation_results)}")

def main():
    # Example validation rules
    validation_rules = {
        'Email': {
            'required': True,
            'type': 'email'
        },
        'Phone': {
            'required': True,
            'type': 'phone'
        },
        'Age': {
            'required': True,
            'type': 'numeric',
            'min': 0,
            'max': 120
        },
        'Status': {
            'required': True,
            'allowed_values': ['Active', 'Inactive', 'Pending']
        }
    }

    validator = ExcelValidator()
    
    # Get file path from user
    file_path = input("Please enter the path to your Excel file: ")
    
    if validator.load_excel(file_path):
        validator.validate_data(validation_rules)
        validator.display_results()

if __name__ == "__main__":
    main() 