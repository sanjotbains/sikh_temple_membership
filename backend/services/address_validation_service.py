"""
Address Validation Service using Google Maps Geocoding API
"""
import os
import requests
from typing import Dict, Optional, Tuple


class AddressValidationService:
    """
    Service for validating addresses using Google Maps Geocoding API
    """

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        self.base_url = 'https://maps.googleapis.com/maps/api/geocode/json'

    def validate_address(
        self,
        address_line1: str,
        address_line2: str = '',
        city: str = '',
        state: str = '',
        postal_code: str = ''
    ) -> Dict:
        """
        Validate an address using Google Maps Geocoding API

        Args:
            address_line1: Street address
            address_line2: Apt/Suite/Unit (optional)
            city: City name
            state: State/Province
            postal_code: ZIP/Postal code

        Returns:
            Dictionary containing:
                - is_valid: Boolean indicating if address is valid
                - formatted_address: Formatted address string from Google
                - confidence: Confidence score (high/medium/low)
                - location: Lat/lng coordinates
                - address_components: Parsed address components
                - suggestions: Suggested corrections if needed
                - error: Error message if validation failed
        """
        if not self.api_key:
            return {
                'is_valid': False,
                'error': 'Google Maps API key not configured',
                'confidence': 'unknown'
            }

        # Build full address string
        address_parts = [address_line1]
        if address_line2:
            address_parts.append(address_line2)
        address_parts.extend([city, state, postal_code])

        # Filter out empty parts
        address_parts = [part.strip() for part in address_parts if part and part.strip()]
        full_address = ', '.join(address_parts)

        if not full_address:
            return {
                'is_valid': False,
                'error': 'No address provided',
                'confidence': 'unknown'
            }

        try:
            # Call Google Maps Geocoding API
            params = {
                'address': full_address,
                'key': self.api_key
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['status'] == 'OK' and data.get('results'):
                result = data['results'][0]

                # Determine confidence based on location type
                location_type = result.get('geometry', {}).get('location_type', '')
                confidence = self._determine_confidence(location_type, result)

                # Parse address components
                parsed_components = self._parse_address_components(result.get('address_components', []))

                # Check if the address matches closely
                is_exact_match = self._is_exact_match(
                    original={
                        'address_line1': address_line1,
                        'city': city,
                        'state': state,
                        'postal_code': postal_code
                    },
                    parsed=parsed_components
                )

                return {
                    'is_valid': True,
                    'formatted_address': result.get('formatted_address', ''),
                    'confidence': confidence,
                    'is_exact_match': is_exact_match,
                    'location': result.get('geometry', {}).get('location', {}),
                    'location_type': location_type,
                    'address_components': parsed_components,
                    'place_id': result.get('place_id', ''),
                    'suggestions': self._generate_suggestions(
                        original={
                            'address_line1': address_line1,
                            'city': city,
                            'state': state,
                            'postal_code': postal_code
                        },
                        parsed=parsed_components
                    ) if not is_exact_match else None
                }

            elif data['status'] == 'ZERO_RESULTS':
                return {
                    'is_valid': False,
                    'error': 'Address not found. Please check the address details.',
                    'confidence': 'invalid'
                }

            elif data['status'] == 'INVALID_REQUEST':
                return {
                    'is_valid': False,
                    'error': 'Invalid address format',
                    'confidence': 'invalid'
                }

            else:
                return {
                    'is_valid': False,
                    'error': f'Validation failed: {data.get("status")}',
                    'confidence': 'unknown'
                }

        except requests.exceptions.Timeout:
            return {
                'is_valid': False,
                'error': 'Request timeout. Please try again.',
                'confidence': 'unknown'
            }

        except requests.exceptions.RequestException as e:
            return {
                'is_valid': False,
                'error': f'Network error: {str(e)}',
                'confidence': 'unknown'
            }

        except Exception as e:
            return {
                'is_valid': False,
                'error': f'Unexpected error: {str(e)}',
                'confidence': 'unknown'
            }

    def _determine_confidence(self, location_type: str, result: Dict) -> str:
        """
        Determine confidence level based on location type

        Location types:
        - ROOFTOP: Most precise (building level)
        - RANGE_INTERPOLATED: Approximate (street level)
        - GEOMETRIC_CENTER: Center of area (e.g., city center)
        - APPROXIMATE: Approximate (e.g., postal code)
        """
        if location_type == 'ROOFTOP':
            return 'high'
        elif location_type in ['RANGE_INTERPOLATED', 'GEOMETRIC_CENTER']:
            return 'medium'
        else:
            return 'low'

    def _parse_address_components(self, components: list) -> Dict:
        """
        Parse Google's address components into a structured format
        """
        parsed = {
            'street_number': '',
            'route': '',
            'locality': '',
            'administrative_area_level_1': '',
            'postal_code': '',
            'country': ''
        }

        for component in components:
            types = component.get('types', [])
            long_name = component.get('long_name', '')
            short_name = component.get('short_name', '')

            if 'street_number' in types:
                parsed['street_number'] = long_name
            elif 'route' in types:
                parsed['route'] = long_name
            elif 'locality' in types:
                parsed['locality'] = long_name
            elif 'administrative_area_level_1' in types:
                parsed['administrative_area_level_1'] = short_name
            elif 'postal_code' in types:
                parsed['postal_code'] = long_name
            elif 'country' in types:
                parsed['country'] = long_name

        return parsed

    def _is_exact_match(self, original: Dict, parsed: Dict) -> bool:
        """
        Check if the parsed address matches the original closely
        """
        # Normalize strings for comparison
        def normalize(s: str) -> str:
            return s.lower().strip() if s else ''

        # Check city
        city_match = normalize(original.get('city', '')) == normalize(parsed.get('locality', ''))

        # Check state (allow both full name and abbreviation)
        state_match = normalize(original.get('state', '')) == normalize(parsed.get('administrative_area_level_1', ''))

        # Check postal code (just first 5 digits for US zip codes)
        orig_zip = normalize(original.get('postal_code', ''))[:5]
        parsed_zip = normalize(parsed.get('postal_code', ''))[:5]
        zip_match = orig_zip == parsed_zip if orig_zip and parsed_zip else True

        # Consider it an exact match if city, state, and zip all match
        return city_match and state_match and zip_match

    def _generate_suggestions(self, original: Dict, parsed: Dict) -> Dict:
        """
        Generate suggestions for address corrections
        """
        suggestions = {}

        # Suggest city correction if different
        if parsed.get('locality') and original.get('city'):
            if parsed['locality'].lower() != original['city'].lower():
                suggestions['city'] = parsed['locality']

        # Suggest state correction if different
        if parsed.get('administrative_area_level_1') and original.get('state'):
            if parsed['administrative_area_level_1'].lower() != original['state'].lower():
                suggestions['state'] = parsed['administrative_area_level_1']

        # Suggest postal code correction if different
        if parsed.get('postal_code') and original.get('postal_code'):
            if parsed['postal_code'][:5] != original['postal_code'][:5]:
                suggestions['postal_code'] = parsed['postal_code']

        return suggestions
