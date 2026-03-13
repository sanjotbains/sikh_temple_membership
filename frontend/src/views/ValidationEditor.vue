<template>
  <div class="validation-editor">
    <!-- Header -->
    <div class="editor-header">
      <button @click="goBack" class="back-btn">
        <i class="pi pi-arrow-left"></i>
        Back to Dashboard
      </button>
      <h1>Validate Submission #{{ submissionId }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Loading submission data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <i class="pi pi-exclamation-triangle" style="font-size: 2rem; color: #ef4444"></i>
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-btn">Retry</button>
    </div>

    <!-- Editor Content -->
    <div v-else class="editor-content">
      <!-- Split Pane Layout -->
      <div class="split-pane">
        <!-- Left Pane - Image Viewer -->
        <div class="pane pane-left">
          <ImageViewer
            v-if="imageUrl"
            :image-url="imageUrl"
            :filename="submission?.file_name"
          />
        </div>

        <!-- Right Pane - Validation Form -->
        <div class="pane pane-right">
          <ValidationForm
            v-if="extractedFields"
            :extracted-fields="extractedFields"
            :submission-id="submissionId"
            :potential-duplicates="potentialDuplicates"
            @save="handleSave"
            @complete="handleComplete"
            @skip="handleSkip"
            @reject="handleReject"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getValidationData, saveValidation, completeValidation, skipValidation, rejectValidation, getImageUrl } from '../services/validationService'
import ImageViewer from '../components/Validation/ImageViewer.vue'
import ValidationForm from '../components/Validation/ValidationForm.vue'

const router = useRouter()
const route = useRoute()

// Get submission ID from route
const submissionId = computed(() => parseInt(route.params.id))

// State
const loading = ref(true)
const error = ref(null)
const submission = ref(null)
const extractedFields = ref(null)
const images = ref([])
const potentialDuplicates = ref([])

// Computed
const imageUrl = computed(() => {
  if (!submission.value || !images.value || images.value.length === 0) {
    console.log('No submission or images available')
    return null
  }
  // Use the first image
  const firstImage = images.value[0]
  const url = getImageUrl(submission.value.id, firstImage.id)
  console.log('ValidationEditor - Computed image URL:', url)
  console.log('Submission ID:', submission.value.id, 'Image ID:', firstImage.id)
  return url
})

// Load data
async function loadData() {
  loading.value = true
  error.value = null

  try {
    const data = await getValidationData(submissionId.value)

    console.log('Loaded validation data:', data)
    console.log('Images:', data.images)

    submission.value = data.submission
    extractedFields.value = data.extracted_fields
    images.value = data.images
    potentialDuplicates.value = data.potential_duplicates || []

    console.log('Potential duplicates found:', potentialDuplicates.value.length)

  } catch (err) {
    console.error('Error loading validation data:', err)
    error.value = 'Failed to load validation data. Please try again.'
  } finally {
    loading.value = false
  }
}

// Handlers
async function handleSave(fields) {
  try {
    await saveValidation(submissionId.value, fields)
    // Show success message (could use a toast notification)
    console.log('Validation saved successfully')
  } catch (err) {
    console.error('Error saving validation:', err)
    alert('Failed to save validation. Please try again.')
  }
}

async function handleComplete(fields) {
  try {
    await completeValidation(submissionId.value, fields, true)
    // Navigate back to dashboard
    router.push('/validation')
  } catch (err) {
    console.error('Error completing validation:', err)
    alert('Failed to complete validation. Please try again.')
  }
}

async function handleSkip() {
  try {
    await skipValidation(submissionId.value)
    // Navigate back to dashboard
    router.push('/validation')
  } catch (err) {
    console.error('Error skipping validation:', err)
    alert('Failed to skip validation. Please try again.')
  }
}

async function handleReject() {
  try {
    await rejectValidation(submissionId.value)
    // Navigate back to dashboard
    router.push('/validation')
  } catch (err) {
    console.error('Error rejecting validation:', err)
    alert('Failed to reject validation. Please try again.')
  }
}

function goBack() {
  router.push('/validation')
}

// Load on mount
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.validation-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
}

.editor-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
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

.back-btn:hover {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

.editor-header h1 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.loading-container,
.error-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.retry-btn {
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

.editor-content {
  flex: 1;
  overflow: hidden;
}

.split-pane {
  display: grid;
  grid-template-columns: 1fr 1fr;
  height: 100%;
  gap: 0;
}

.pane {
  overflow: auto;
  background: white;
}

.pane-left {
  border-right: 1px solid #e5e7eb;
}

@media (max-width: 1024px) {
  .split-pane {
    grid-template-columns: 1fr;
    grid-template-rows: 400px 1fr;
  }

  .pane-left {
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
}
</style>
