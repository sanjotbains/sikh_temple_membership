/**
 * Address Validation Service
 * Handles address validation via backend API
 */
import api from './api'

/**
 * Validate an address
 * @param {Object} address - Address object with fields
 * @param {string} address.address_line1 - Street address
 * @param {string} address.address_line2 - Apt/Suite/Unit (optional)
 * @param {string} address.city - City name
 * @param {string} address.state - State/Province
 * @param {string} address.postal_code - ZIP/Postal code
 * @returns {Promise<Object>} Validation result
 */
export async function validateAddress(address) {
  try {
    const response = await api.post('/validation/validate-address', address)
    return response.data
  } catch (error) {
    console.error('Address validation error:', error)
    throw error
  }
}

export default {
  validateAddress
}
