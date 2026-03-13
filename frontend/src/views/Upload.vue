<template>
  <div class="upload-view">
    <div class="page-header">
      <h1>Upload Forms</h1>
      <p>Upload scanned membership forms (PDF or images) for OCR processing.</p>
    </div>

    <!-- File Uploader Component -->
    <FileUploader
      @upload-complete="handleUploadComplete"
      @ocr-started="handleOCRStarted"
    />

    <!-- OCR Processing Status -->
    <div v-if="isProcessingOCR" class="ocr-status">
      <div class="status-card">
        <i class="pi pi-spin pi-spinner status-icon"></i>
        <h3>Processing OCR...</h3>
        <p>Extracting text from uploaded forms. This may take a few moments.</p>
        <div class="processing-info">
          <span>{{ ocrProcessedCount }} of {{ ocrTotalCount }} forms processed</span>
        </div>
      </div>
    </div>

    <!-- Recent Uploads -->
    <div v-if="recentBatches.length > 0" class="recent-uploads">
      <h2>Recent Uploads</h2>
      <div class="batch-list">
        <div v-for="batch in recentBatches" :key="batch.batch_id" class="batch-card">
          <div class="batch-header">
            <h3>Batch: {{ batch.batch_id.substring(0, 8) }}...</h3>
            <span class="batch-count">{{ batch.submissions.length }} files</span>
          </div>
          <div class="batch-details">
            <p><strong>Uploaded:</strong> {{ formatDate(batch.uploaded_at) }}</p>
            <div class="batch-stats">
              <span class="stat-badge pending" v-if="getPendingCount(batch) > 0">
                <i class="pi pi-clock"></i>
                {{ getPendingCount(batch) }} Pending
              </span>
              <span class="stat-badge completed" v-if="getCompletedCount(batch) > 0">
                <i class="pi pi-check"></i>
                {{ getCompletedCount(batch) }} OCR Complete
              </span>
            </div>
          </div>
          <button class="btn btn-primary btn-sm" @click="viewBatch(batch.batch_id)">
            View Submissions
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FileUploader from '@/components/Upload/FileUploader.vue'
import { getBatchSubmissions } from '@/services/uploadService'

const router = useRouter()

// State
const isProcessingOCR = ref(false)
const ocrProcessedCount = ref(0)
const ocrTotalCount = ref(0)
const recentBatches = ref([])

// Handlers
function handleUploadComplete(result) {
  console.log('Upload complete:', result)

  // Add to recent batches
  if (result.batch_id) {
    loadBatch(result.batch_id)
  }
}

function handleOCRStarted(result) {
  console.log('OCR started:', result)
  isProcessingOCR.value = true
  ocrTotalCount.value = result.submissions ? result.submissions.length : 0
  ocrProcessedCount.value = 0

  // Simulate progress (in real app, would poll backend for status)
  simulateOCRProgress()
}

function simulateOCRProgress() {
  const interval = setInterval(() => {
    if (ocrProcessedCount.value < ocrTotalCount.value) {
      ocrProcessedCount.value++
    } else {
      clearInterval(interval)
      isProcessingOCR.value = false
      // Refresh batches
      loadRecentBatches()
    }
  }, 2000)
}

async function loadBatch(batchId) {
  try {
    const data = await getBatchSubmissions(batchId)
    const existingIndex = recentBatches.value.findIndex(b => b.batch_id === batchId)

    if (existingIndex >= 0) {
      recentBatches.value[existingIndex] = data
    } else {
      recentBatches.value.unshift(data)
    }

    // Keep only last 5 batches
    if (recentBatches.value.length > 5) {
      recentBatches.value = recentBatches.value.slice(0, 5)
    }
  } catch (error) {
    console.error('Error loading batch:', error)
  }
}

function loadRecentBatches() {
  // In a real app, would fetch from backend
  // For now, just refresh existing batches
  recentBatches.value.forEach(batch => {
    loadBatch(batch.batch_id)
  })
}

function viewBatch(batchId) {
  // Navigate to validation dashboard with batch filter
  router.push({ name: 'validation', query: { batch: batchId } })
}

function formatDate(dateString) {
  if (!dateString) return 'Just now'
  const date = new Date(dateString)
  return date.toLocaleString()
}

function getPendingCount(batch) {
  if (!batch.submissions) return 0
  return batch.submissions.filter(s => s.ocr_status === 'pending').length
}

function getCompletedCount(batch) {
  if (!batch.submissions) return 0
  return batch.submissions.filter(s => s.ocr_status === 'completed').length
}

onMounted(() => {
  // Load recent batches on mount (if any stored)
})
</script>

<style scoped>
.upload-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
}

.page-header p {
  margin: 0;
  color: #718096;
  font-size: 1.1rem;
}

.ocr-status {
  margin: 2rem 0;
}

.status-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.status-icon {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.status-card h3 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
}

.status-card p {
  margin: 0 0 1rem 0;
  color: #718096;
}

.processing-info {
  padding: 1rem;
  background: #ebf4ff;
  border-radius: 6px;
  color: #2c5282;
  font-weight: 600;
}

.recent-uploads {
  margin-top: 3rem;
}

.recent-uploads h2 {
  margin: 0 0 1.5rem 0;
  color: #2d3748;
}

.batch-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.batch-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.batch-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.batch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.batch-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1rem;
}

.batch-count {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.batch-details {
  margin-bottom: 1rem;
}

.batch-details p {
  margin: 0 0 0.75rem 0;
  color: #718096;
  font-size: 0.9rem;
}

.batch-stats {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.stat-badge.pending {
  background: #fefcbf;
  color: #744210;
}

.stat-badge.completed {
  background: #c6f6d5;
  color: #22543d;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}
</style>
