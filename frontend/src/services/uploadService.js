/**
 * Upload service for file uploads and submission management
 */
import api from './api'
import axios from 'axios'

/**
 * Upload files to the server
 * @param {FileList} files - Files to upload
 * @param {Function} onProgress - Progress callback
 * @param {Boolean} splitPdfPages - If true, split multi-page PDFs into separate submissions
 * @returns {Promise} Upload response
 */
export async function uploadFiles(files, onProgress, splitPdfPages = false) {
  const formData = new FormData()

  // Add all files to form data
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i])
  }

  // Add split_pdf_pages option
  if (splitPdfPages) {
    formData.append('split_pdf_pages', 'true')
  }

  // Upload with progress tracking
  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentCompleted)
      }
    }
  })

  return response.data
}

/**
 * Get all submissions with filtering
 * @param {Object} filters - Filter options
 * @returns {Promise} List of submissions
 */
export async function getSubmissions(filters = {}) {
  const response = await api.get('/submissions/', { params: filters })
  return response.data
}

/**
 * Get a single submission by ID
 * @param {Number} submissionId - Submission ID
 * @returns {Promise} Submission details
 */
export async function getSubmission(submissionId) {
  const response = await api.get(`/submissions/${submissionId}`)
  return response.data
}

/**
 * Get submissions for a batch
 * @param {String} batchId - Batch ID
 * @returns {Promise} Batch submissions
 */
export async function getBatchSubmissions(batchId) {
  const response = await api.get(`/upload/batch/${batchId}`)
  return response.data
}

/**
 * Get pending submissions that need OCR
 * @param {Number} limit - Maximum number of results
 * @returns {Promise} List of pending submissions
 */
export async function getPendingSubmissions(limit = 50) {
  const response = await api.get('/upload/pending', { params: { limit } })
  return response.data
}

/**
 * Trigger OCR processing for a submission
 * @param {Number} submissionId - Submission ID
 * @returns {Promise} OCR results
 */
export async function processOCR(submissionId) {
  const response = await api.post(`/upload/process-ocr/${submissionId}`)
  return response.data
}

/**
 * Get OCR results for a submission
 * @param {Number} submissionId - Submission ID
 * @returns {Promise} OCR results
 */
export async function getOCRResults(submissionId) {
  const response = await api.get(`/submissions/${submissionId}/ocr`)
  return response.data
}

/**
 * Get extracted fields for a submission
 * @param {Number} submissionId - Submission ID
 * @returns {Promise} Extracted fields
 */
export async function getExtractedFields(submissionId) {
  const response = await api.get(`/submissions/${submissionId}/extracted-fields`)
  return response.data
}

/**
 * Get image URL for display
 * @param {Number} submissionId - Submission ID
 * @param {Number} imageId - Image ID
 * @returns {String} Image URL
 */
export function getImageUrl(submissionId, imageId) {
  return `/api/submissions/${submissionId}/image/${imageId}`
}

/**
 * Update submission status
 * @param {Number} submissionId - Submission ID
 * @param {Object} statusUpdates - Status fields to update
 * @returns {Promise} Updated submission
 */
export async function updateSubmissionStatus(submissionId, statusUpdates) {
  const response = await api.put(`/submissions/${submissionId}/status`, statusUpdates)
  return response.data
}

/**
 * Get submission statistics
 * @returns {Promise} Statistics object
 */
export async function getSubmissionStats() {
  const response = await api.get('/submissions/stats')
  return response.data
}
