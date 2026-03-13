/**
 * Member Service - API calls for member management
 */
import api from './api'

/**
 * Get members with optional search and filtering
 */
export async function getMembers(params = {}) {
  const response = await api.get('/members/', { params })
  return response.data
}

/**
 * Get a single member by ID
 */
export async function getMember(memberId) {
  const response = await api.get(`/members/${memberId}`)
  return response.data
}

/**
 * Update a member
 */
export async function updateMember(memberId, data) {
  const response = await api.put(`/members/${memberId}`, data)
  return response.data
}

/**
 * Delete a member (soft delete - marks as inactive)
 */
export async function deleteMember(memberId) {
  const response = await api.delete(`/members/${memberId}`)
  return response.data
}

/**
 * Reject a member (marks member and submissions as rejected)
 */
export async function rejectMember(memberId, reason = '') {
  const response = await api.post(`/members/${memberId}/reject`, {
    reason
  })
  return response.data
}

/**
 * Get member statistics
 */
export async function getMemberStats() {
  const response = await api.get('/members/stats')
  return response.data
}

/**
 * Get search suggestions (cities, states)
 */
export async function getSearchSuggestions() {
  const response = await api.get('/members/search-suggestions')
  return response.data
}

/**
 * Export members to Excel or CSV
 */
export async function exportMembers(format = 'excel', memberIds = [], filters = {}) {
  const response = await api.post('/export/members', {
    format,
    member_ids: memberIds,
    filters
  }, {
    responseType: 'blob'  // Important for file download
  })

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url

  // Get filename from Content-Disposition header or use default
  const contentDisposition = response.headers['content-disposition']
  let filename = format === 'csv' ? 'members_export.csv' : 'members_export.xlsx'

  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/)
    if (filenameMatch) {
      filename = filenameMatch[1]
    }
  }

  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)

  return { success: true, filename }
}

/**
 * Download sample import template
 */
export async function downloadSampleTemplate() {
  const response = await api.get('/export/sample', {
    responseType: 'blob'
  })

  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'member_import_template.csv')
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)

  return { success: true }
}
