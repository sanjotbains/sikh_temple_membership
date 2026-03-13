"""
Date parsing utility functions
"""
import re
from datetime import datetime
from dateutil import parser as date_parser


def parse_date(text):
    """
    Parse date from text using various formats

    Args:
        text: Text containing potential date

    Returns:
        dict: {'date': datetime or None, 'formatted': str, 'confidence': float}
    """
    if not text:
        return {'date': None, 'formatted': '', 'confidence': 0.0}

    # Common date patterns
    patterns = [
        (r'(\d{1,2})/(\d{1,2})/(\d{4})', 'MM/DD/YYYY'),      # 12/31/2023
        (r'(\d{1,2})-(\d{1,2})-(\d{4})', 'MM-DD-YYYY'),      # 12-31-2023
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', 'YYYY-MM-DD'),      # 2023-12-31
        (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', 'MM.DD.YYYY'),    # 12.31.2023
    ]

    # Try each pattern
    for pattern, format_name in patterns:
        matches = re.findall(pattern, text)
        if matches:
            try:
                # Try to parse the matched date
                if format_name == 'YYYY-MM-DD':
                    year, month, day = matches[0]
                else:
                    month, day, year = matches[0]

                date_obj = datetime(int(year), int(month), int(day))

                return {
                    'date': date_obj,
                    'formatted': date_obj.strftime('%Y-%m-%d'),
                    'confidence': 0.9
                }
            except (ValueError, IndexError):
                continue

    # Try dateutil parser as fallback (more flexible but less reliable)
    try:
        parsed_date = date_parser.parse(text, fuzzy=True)
        # Only accept if year is reasonable (1900-2100)
        if 1900 <= parsed_date.year <= 2100:
            return {
                'date': parsed_date,
                'formatted': parsed_date.strftime('%Y-%m-%d'),
                'confidence': 0.6
            }
    except (ValueError, OverflowError):
        pass

    return {'date': None, 'formatted': '', 'confidence': 0.0}


def is_valid_dob(date_obj):
    """
    Check if a date is a valid date of birth (not in the future, not too old)

    Args:
        date_obj: datetime object

    Returns:
        bool: True if valid DOB
    """
    if not date_obj:
        return False

    now = datetime.now()
    age = (now - date_obj).days / 365.25

    # Valid if between 0 and 120 years old
    return 0 <= age <= 120
