/**
 * Validation Service - API calls for validation workflow
 */
import api from './api'

/**
 * Get pending validations
 */
export async function getPendingValidations(limit = 20, offset = 0) {
  const response = await api.get('/validation/pending', {
    params: { limit, offset }
  })
  return response.data
}

/**
 * Get validation data for a specific submission
 */
export async function getValidationData(submissionId) {
  const response = await api.get(`/validation/${submissionId}`)
  return response.data
}

/**
 * Get image URL for a submission
 */
export function getImageUrl(submissionId, imageId) {
  return `/api/submissions/${submissionId}/image/${imageId}`
}

/**
 * Save validated fields (without completing validation)
 */
export async function saveValidation(submissionId, fields) {
  const response = await api.post(`/validation/${submissionId}/save`, {
    fields
  })
  return response.data
}

/**
 * Complete validation and create member record
 */
export async function completeValidation(submissionId, fields, createMember = true) {
  const response = await api.post(`/validation/${submissionId}/complete`, {
    fields,
    create_member: createMember
  })
  return response.data
}

/**
 * Skip validation for this submission
 */
export async function skipValidation(submissionId) {
  const response = await api.post(`/validation/${submissionId}/skip`)
  return response.data
}

/**
 * Reject/discard an invalid submission
 */
export async function rejectValidation(submissionId, reason = '') {
  const response = await api.post(`/validation/${submissionId}/reject`, {
    reason
  })
  return response.data
}

/**
 * Get validation statistics
 */
export async function getValidationStats() {
  const response = await api.get('/validation/stats')
  return response.data
}
