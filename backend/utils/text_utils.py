"""
Text utility functions for processing and extracting information from OCR text
"""
import re
import phonenumbers


def normalize_text(text):
    """
    Normalize text by removing extra whitespace and standardizing format

    Args:
        text: Raw text string

    Returns:
        str: Normalized text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove special characters that might interfere
    text = text.strip()

    return text


def extract_name(text):
    """
    Extract name from text using heuristics

    Args:
        text: Text containing potential name

    Returns:
        dict: {'first_name': str, 'last_name': str, 'full_name': str, 'confidence': float}
    """
    if not text:
        return {'first_name': '', 'last_name': '', 'full_name': '', 'confidence': 0.0}

    lines = text.split('\n')

    # Look for lines immediately after "1. Name:" label (membership form specific)
    for idx, line in enumerate(lines):
        if re.match(r'^\s*1\.\s*Name', line, re.IGNORECASE):
            # Get the next 1-3 lines after the label
            name_lines = []
            for i in range(1, 4):
                if idx + i < len(lines):
                    next_line = lines[idx + i].strip()
                    # Stop if we hit another numbered item or section
                    if re.match(r'^\d+\.', next_line) or not next_line:
                        break
                    # Filter out common non-name content
                    if not any(word in next_line.upper() for word in ['TEMPLE', 'APPLICATION', 'PLEASE', 'ADDRESS', 'PHONE']):
                        name_lines.append(next_line)

            if name_lines:
                # Combine name lines (could be multiple lines for first/last name)
                full_name = ' '.join(name_lines)
                parts = full_name.split()

                # Try to identify first name and last name
                if len(parts) >= 3:
                    # Assume first name, middle name/initial, last name
                    return {
                        'first_name': ' '.join(parts[:2]),  # First + middle as first name
                        'last_name': ' '.join(parts[2:]),
                        'full_name': full_name,
                        'confidence': 0.9
                    }
                elif len(parts) >= 2:
                    return {
                        'first_name': parts[0],
                        'last_name': ' '.join(parts[1:]),
                        'full_name': full_name,
                        'confidence': 0.9
                    }

    # Look for generic "Name:" label
    for line in lines:
        if 'name' in line.lower() and ':' in line:
            name_text = line.split(':', 1)[1].strip()
            if name_text and len(name_text) > 3:  # Ensure it's not empty
                parts = name_text.split()
                if len(parts) >= 2:
                    return {
                        'first_name': parts[0],
                        'last_name': ' '.join(parts[1:]),
                        'full_name': name_text,
                        'confidence': 0.7
                    }

    return {'first_name': '', 'last_name': '', 'full_name': '', 'confidence': 0.0}


def extract_phone(text):
    """
    Extract phone number from text

    Args:
        text: Text containing potential phone number

    Returns:
        dict: {'phone': str, 'formatted': str, 'confidence': float}
    """
    if not text:
        return {'phone': '', 'formatted': '', 'confidence': 0.0}

    lines = text.split('\n')

    # Look for "4. Phone Number" pattern (membership form specific)
    for idx, line in enumerate(lines):
        if re.match(r'^\s*4\.\s*Phone\s+Number', line, re.IGNORECASE):
            # Check next 1-2 lines for phone number
            for i in range(1, 3):
                if idx + i < len(lines):
                    phone_line = lines[idx + i].strip()
                    phone_data = _extract_phone_from_line(phone_line)
                    if phone_data['phone']:
                        phone_data['confidence'] = 0.9
                        return phone_data

    # Try to find phone in all text
    phone_data = _extract_phone_from_line(text)
    if phone_data['phone']:
        return phone_data

    return {'phone': '', 'formatted': '', 'confidence': 0.0}


def _extract_phone_from_line(text):
    """Helper function to extract phone from a line of text"""
    # Phone number patterns
    patterns = [
        r'\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # (123) 456-7890 or 123-456-7890
        r'(\d{3})[-.\s]?(\d{3})[-.\s]?(\d{4})',         # 123 456 7890
        r'(\d{10})',                                     # 1234567890
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            if isinstance(matches[0], tuple):
                phone_digits = ''.join(matches[0])
            else:
                phone_digits = matches[0]

            # Try to parse with phonenumbers library
            try:
                parsed = phonenumbers.parse(phone_digits, "US")  # Default to US
                if phonenumbers.is_valid_number(parsed):
                    formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
                    return {
                        'phone': phone_digits,
                        'formatted': formatted,
                        'confidence': 0.9
                    }
            except:
                pass

            # If parsing fails, just return the digits
            if len(phone_digits) == 10:
                formatted = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
                return {
                    'phone': phone_digits,
                    'formatted': formatted,
                    'confidence': 0.7
                }

    return {'phone': '', 'formatted': '', 'confidence': 0.0}


def extract_address(text):
    """
    Extract address from text

    Args:
        text: Text containing potential address

    Returns:
        dict: {'address_line1': str, 'address_line2': str, 'city': str,
               'state': str, 'postal_code': str, 'confidence': float}
    """
    if not text:
        return {
            'address_line1': '',
            'address_line2': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'confidence': 0.0
        }

    lines = text.split('\n')

    # Look for "2. Complete Primary Residence Address" (membership form specific)
    for idx, line in enumerate(lines):
        if re.match(r'^\s*2\.\s*(Complete\s+)?Primary\s+Residence\s+Address', line, re.IGNORECASE):
            # Get the next 2-4 lines after the label
            address_line1 = ''
            city = ''
            state = ''
            postal_code = ''

            # Check next few lines
            for i in range(1, 6):
                if idx + i >= len(lines):
                    break

                next_line = lines[idx + i].strip()

                # Stop if we hit another numbered item (but not 3. Mailing Address)
                if re.match(r'^\d+\.', next_line) and 'mail' not in next_line.lower():
                    break

                # Skip instruction text
                if any(word in next_line.upper() for word in ['MUST INCLUDE', 'CITY', 'ZIP CODE', 'DIFFERENT']):
                    continue

                # First valid line is street address
                if not address_line1 and next_line and len(next_line) > 3:
                    address_line1 = next_line
                    continue

                # Look for city and state (usually "CITY STATE" or "CITY, STATE")
                if not city and address_line1:
                    # Check if this line has city and state (2 words, no numbers)
                    parts = re.split(r'[,\s]+', next_line)
                    if len(parts) >= 2 and not re.search(r'\d', next_line):
                        city = ' '.join(parts[:-1])
                        state = parts[-1]
                        continue

                # Look for ZIP code (5 digits)
                zip_match = re.search(r'\b\d{5}(-\d{4})?\b', next_line)
                if zip_match and not postal_code:
                    postal_code = zip_match.group()

            if address_line1:
                return {
                    'address_line1': address_line1,
                    'address_line2': '',
                    'city': city,
                    'state': state,
                    'postal_code': postal_code,
                    'confidence': 0.9
                }

    # Look for postal code (Canadian format: A1A 1A1 or US format: 12345)
    us_postal_pattern = r'\b\d{5}(-\d{4})?\b'
    ca_postal_pattern = r'[A-Z]\d[A-Z]\s?\d[A-Z]\d'
    postal_code = ''
    postal_line_idx = -1

    # Try US format first
    for idx, line in enumerate(lines):
        match = re.search(us_postal_pattern, line)
        if match:
            postal_code = match.group()
            postal_line_idx = idx
            break

    # Try Canadian format
    if not postal_code:
        for idx, line in enumerate(lines):
            match = re.search(ca_postal_pattern, line.upper())
            if match:
                postal_code = match.group()
                postal_line_idx = idx
                break

    # If we found postal code, try to extract address components
    if postal_line_idx > 0:
        # Address line 1 might be 1-2 lines before postal code
        address_line1 = lines[postal_line_idx - 1].strip() if postal_line_idx > 0 else ''

        # City and state might be on the same line as postal code
        city_state_line = lines[postal_line_idx]
        # Remove postal code from line
        city_state_text = re.sub(us_postal_pattern if postal_code.isdigit() or '-' in postal_code else ca_postal_pattern,
                                 '', city_state_line, flags=re.IGNORECASE).strip()
        parts = re.split(r'[,\s]+', city_state_text)

        city = parts[0] if len(parts) > 0 else ''
        state = parts[-1] if len(parts) > 1 else ''

        return {
            'address_line1': address_line1,
            'address_line2': '',
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'confidence': 0.7
        }

    return {
        'address_line1': '',
        'address_line2': '',
        'city': '',
        'state': '',
        'postal_code': '',
        'confidence': 0.0
    }


def extract_email(text):
    """
    Extract email address from text

    Args:
        text: Text containing potential email

    Returns:
        dict: {'email': str, 'confidence': float}
    """
    if not text:
        return {'email': '', 'confidence': 0.0}

    # Email pattern
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, text)

    if matches:
        return {
            'email': matches[0],
            'confidence': 0.9
        }

    return {'email': '', 'confidence': 0.0}
