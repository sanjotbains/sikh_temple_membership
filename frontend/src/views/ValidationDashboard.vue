<template>
  <div class="validation-dashboard">
    <div class="dashboard-header">
      <h1>Validation Dashboard</h1>
      <p class="subtitle">Review and correct OCR-extracted data from membership forms</p>
    </div>

    <!-- Stats Cards -->
    <div class="stats-cards" v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.pending }}</div>
        <div class="stat-label">Pending Validation</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.in_progress }}</div>
        <div class="stat-label">In Progress</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.completed }}</div>
        <div class="stat-label">Completed</div>
      </div>
      <div class="stat-card alert" v-if="pendingOcrCount > 0">
        <div class="stat-value">{{ pendingOcrCount }}</div>
        <div class="stat-label">Needs OCR Processing</div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Loading submissions...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <i class="pi pi-exclamation-triangle" style="font-size: 2rem; color: #ef4444"></i>
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-btn">Retry</button>
    </div>

    <!-- Pending OCR Banner -->
    <div v-if="pendingOcrCount > 0" class="pending-ocr-section">
      <div class="section-header alert-header">
        <div>
          <h2>
            <i class="pi pi-exclamation-triangle"></i>
            {{ pendingOcrCount }} Submission{{ pendingOcrCount !== 1 ? 's' : '' }} Awaiting OCR Processing
          </h2>
          <p>These submissions were uploaded but haven't been processed yet</p>
        </div>
        <button
          @click="processAllPendingOCR"
          class="btn btn-primary"
          :disabled="isProcessingOCR"
        >
          <i :class="isProcessingOCR ? 'pi pi-spin pi-spinner' : 'pi pi-bolt'"></i>
          {{ isProcessingOCR ? 'Processing...' : 'Process All OCR' }}
        </button>
      </div>
    </div>

    <!-- Failed OCR Banner -->
    <div v-if="failedOcrCount > 0" class="failed-ocr-section">
      <div class="section-header alert-header failed-header">
        <div>
          <h2>
            <i class="pi pi-times-circle"></i>
            {{ failedOcrCount }} Submission{{ failedOcrCount !== 1 ? 's' : '' }} Failed OCR Processing
          </h2>
          <p>These submissions have no usable OCR data — either the processing errored out or completed without extracting any text (e.g. due to a Google Cloud billing issue). Reset and retry once your account is restored.</p>
        </div>
        <button
          @click="retryFailedOCR"
          class="btn btn-danger"
          :disabled="isRetryingFailedOCR"
        >
          <i :class="isRetryingFailedOCR ? 'pi pi-spin pi-spinner' : 'pi pi-refresh'"></i>
          {{ isRetryingFailedOCR ? 'Retrying...' : 'Retry Failed OCR' }}
        </button>
      </div>
      <div class="failed-submissions-list">
        <div
          v-for="submission in failedOcrSubmissions"
          :key="submission.id"
          class="failed-submission-row"
        >
          <span class="submission-id">#{{ submission.id }}</span>
          <span class="submission-filename">{{ submission.file_name }}</span>
          <span class="error-message">{{ submission.error_message || 'OCR error' }}</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !error && submissions.length === 0 && pendingOcrCount === 0 && failedOcrCount === 0" class="empty-state">
      <i class="pi pi-check-circle" style="font-size: 3rem; color: #10b981"></i>
      <h3>All caught up!</h3>
      <p>There are no submissions pending validation at the moment.</p>
    </div>

    <!-- Submissions List -->
    <div v-if="submissions.length > 0" class="submissions-container">
      <div class="submissions-header">
        <h2>Pending Validations ({{ total }})</h2>
      </div>

      <div class="submissions-list">
        <div
          v-for="submission in submissions"
          :key="submission.id"
          class="submission-card"
          @click="openValidation(submission.id)"
        >
          <div class="submission-info">
            <div class="submission-id">#{{ submission.id }}</div>
            <div class="submission-filename">{{ submission.file_name }}</div>
            <div class="submission-date">
              <i class="pi pi-clock"></i>
              Uploaded {{ formatDate(submission.uploaded_at) }}
            </div>
          </div>

          <div class="submission-status">
            <span class="status-badge" :class="`status-${submission.ocr_status}`">
              OCR: {{ submission.ocr_status }}
            </span>
            <span class="status-badge" :class="`status-${submission.validation_status}`">
              Validation: {{ submission.validation_status }}
            </span>
          </div>

          <div class="submission-action">
            <button class="validate-btn">
              <i class="pi pi-pencil"></i>
              Validate
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > limit" class="pagination">
        <button
          @click="previousPage"
          :disabled="offset === 0"
          class="page-btn"
        >
          <i class="pi pi-chevron-left"></i>
          Previous
        </button>
        <span class="page-info">
          Showing {{ offset + 1 }} - {{ Math.min(offset + limit, total) }} of {{ total }}
        </span>
        <button
          @click="nextPage"
          :disabled="offset + limit >= total"
          class="page-btn"
        >
          Next
          <i class="pi pi-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPendingValidations, getValidationStats } from '../services/validationService'
import { getPendingSubmissions, processOCR, getFailedOcrSubmissions, resetFailedOcr } from '../services/uploadService'

const router = useRouter()

// State
const loading = ref(true)
const error = ref(null)
const submissions = ref([])
const stats = ref(null)
const total = ref(0)
const limit = ref(20)
const offset = ref(0)

// Pending OCR state
const pendingOcrSubmissions = ref([])
const pendingOcrCount = ref(0)
const isProcessingOCR = ref(false)

// Failed OCR state
const failedOcrSubmissions = ref([])
const failedOcrCount = ref(0)
const isRetryingFailedOCR = ref(false)

// Load data
async function loadData() {
  loading.value = true
  error.value = null

  try {
    // Load stats, submissions, and pending OCR in parallel
    const [submissionsData, statsData, pendingOcrData] = await Promise.all([
      getPendingValidations(limit.value, offset.value),
      getValidationStats(),
      getPendingSubmissions(1000) // Load pending OCR submissions for processing
    ])

    submissions.value = submissionsData.submissions
    total.value = submissionsData.total
    stats.value = statsData

    // Load pending OCR submissions
    pendingOcrSubmissions.value = pendingOcrData.submissions || []
    pendingOcrCount.value = pendingOcrData.count || 0

    // Load failed OCR submissions
    const failedOcrData = await getFailedOcrSubmissions()
    failedOcrSubmissions.value = failedOcrData.submissions || []
    failedOcrCount.value = failedOcrData.count || 0

  } catch (err) {
    console.error('Error loading validation data:', err)
    error.value = 'Failed to load validation data. Please try again.'
  } finally {
    loading.value = false
  }
}

// Process all pending OCR submissions
async function processAllPendingOCR() {
  if (pendingOcrSubmissions.value.length === 0) return

  isProcessingOCR.value = true

  try {
    // Process all fetched submissions sequentially, reloading in batches
    let remaining = [...pendingOcrSubmissions.value]
    while (remaining.length > 0) {
      for (const submission of remaining) {
        try {
          await processOCR(submission.id)
        } catch (err) {
          console.error(`Failed to process OCR for submission ${submission.id}:`, err)
        }
      }
      // Reload and check if more remain
      const nextBatch = await getPendingSubmissions(1000)
      remaining = nextBatch.submissions || []
    }

    await loadData()
  } catch (err) {
    console.error('Error processing OCR batch:', err)
    alert('Some OCR processing failed. Please check the submissions.')
  } finally {
    isProcessingOCR.value = false
  }
}

// Retry all failed OCR submissions
async function retryFailedOCR() {
  if (failedOcrSubmissions.value.length === 0) return

  isRetryingFailedOCR.value = true

  try {
    await resetFailedOcr()
    // Now process them via the existing OCR pipeline
    const nextBatch = await getPendingSubmissions(1000)
    pendingOcrSubmissions.value = nextBatch.submissions || []

    let remaining = [...pendingOcrSubmissions.value]
    while (remaining.length > 0) {
      for (const submission of remaining) {
        try {
          await processOCR(submission.id)
        } catch (err) {
          console.error(`Failed to process OCR for submission ${submission.id}:`, err)
        }
      }
      const nextBatch = await getPendingSubmissions(1000)
      remaining = nextBatch.submissions || []
    }

    await loadData()
  } catch (err) {
    console.error('Error retrying failed OCR:', err)
    alert('Some OCR retries failed. Please check the submissions.')
  } finally {
    isRetryingFailedOCR.value = false
  }
}

// Pagination
function previousPage() {
  if (offset.value > 0) {
    offset.value = Math.max(0, offset.value - limit.value)
    loadData()
  }
}

function nextPage() {
  if (offset.value + limit.value < total.value) {
    offset.value += limit.value
    loadData()
  }
}

// Navigate to validation editor
function openValidation(submissionId) {
  router.push(`/validation/${submissionId}`)
}

// Format date
function formatDate(dateString) {
  if (!dateString) return 'Unknown'

  // Backend returns UTC timestamps without 'Z', so add it for proper parsing
  const isoString = dateString.includes('Z') ? dateString : dateString + 'Z'
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  return date.toLocaleDateString()
}

// Load on mount
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.validation-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6b7280;
  font-size: 1rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #6b7280;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.loading-container,
.error-container,
.empty-state {
  background: white;
  border-radius: 8px;
  padding: 4rem 2rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.error-container p,
.empty-state p {
  margin-top: 1rem;
  color: #6b7280;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
}

.retry-btn:hover {
  background: #5568d3;
}

.submissions-container {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.submissions-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.submission-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.submission-card:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.submission-info {
  flex: 1;
}

.submission-id {
  font-weight: 600;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.submission-filename {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.submission-date {
  font-size: 0.875rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.submission-status {
  display: flex;
  gap: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-error {
  background: #fee2e2;
  color: #991b1b;
}

.validate-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
}

.validate-btn:hover {
  background: #5568d3;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
}

.page-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 0.875rem;
}

/* Pending OCR Section */
.pending-ocr-section {
  background: #fffbeb;
  border: 2px solid #fbbf24;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.alert-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alert-header p {
  color: #78350f;
  font-size: 0.875rem;
  margin: 0;
}

.stat-card.alert {
  background: #fffbeb;
  border: 2px solid #fbbf24;
}

.stat-card.alert .stat-value {
  color: #f59e0b;
}

.stat-card.alert .stat-label {
  color: #78350f;
}


.section-header {
  margin-bottom: 1rem;
}

.failed-ocr-section {
  background: #fff1f2;
  border: 2px solid #f87171;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.failed-header h2 {
  color: #991b1b;
}

.failed-header p {
  color: #7f1d1d;
  font-size: 0.875rem;
  margin: 0;
}

.failed-submissions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.failed-submission-row {
  display: flex;
  gap: 1rem;
  align-items: baseline;
  font-size: 0.875rem;
  padding: 0.4rem 0.5rem;
  background: #fee2e2;
  border-radius: 4px;
}

.failed-submission-row .submission-id {
  font-weight: 600;
  color: #991b1b;
  flex-shrink: 0;
}

.failed-submission-row .submission-filename {
  color: #1f2937;
  flex-shrink: 0;
}

.failed-submission-row .error-message {
  color: #b91c1c;
  font-style: italic;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
}
</style>
