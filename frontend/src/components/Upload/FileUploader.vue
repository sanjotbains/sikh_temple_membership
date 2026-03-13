<template>
  <div class="file-uploader">
    <div
      class="upload-area"
      :class="{ 'drag-over': isDragging, 'uploading': isUploading }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        accept=".pdf,.jpg,.jpeg,.png,.tiff"
        @change="handleFileSelect"
        style="display: none"
      />

      <div v-if="!isUploading" class="upload-prompt">
        <i class="pi pi-cloud-upload upload-icon"></i>
        <h3>Drag & Drop Files Here</h3>
        <p>or click to browse</p>
        <p class="file-types">Accepted: PDF, JPG, PNG, TIFF</p>
      </div>

      <div v-else class="upload-progress">
        <i class="pi pi-spin pi-spinner progress-icon"></i>
        <h3>Uploading...</h3>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <p>{{ uploadProgress }}%</p>
      </div>
    </div>

    <!-- Selected Files List -->
    <div v-if="selectedFiles.length > 0 && !isUploading" class="files-list">
      <h4>Selected Files ({{ selectedFiles.length }})</h4>
      <div class="file-item" v-for="(file, index) in selectedFiles" :key="index">
        <i class="pi pi-file file-icon"></i>
        <div class="file-info">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
        </div>
        <i class="pi pi-times remove-icon" @click="removeFile(index)"></i>
      </div>

      <!-- Upload Options -->
      <div class="upload-options">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="splitPdfPages"
            :disabled="isUploading || !hasPdfFiles"
          />
          <span>Split multi-page PDFs into separate submissions (one per page)</span>
        </label>
        <p class="option-help" v-if="hasPdfFiles">
          <i class="pi pi-info-circle"></i>
          Useful when scanning multiple forms with an ADF scanner
        </p>
      </div>

      <div class="upload-actions">
        <button class="btn btn-primary" @click="uploadFiles" :disabled="isUploading">
          <i class="pi pi-upload"></i>
          Upload Files
        </button>
        <button class="btn btn-secondary" @click="clearFiles" :disabled="isUploading">
          <i class="pi pi-times"></i>
          Clear All
        </button>
      </div>
    </div>

    <!-- Upload Results -->
    <div v-if="uploadResult" class="upload-result">
      <div class="success-message" v-if="uploadResult.success_count > 0">
        <i class="pi pi-check-circle"></i>
        <span>Successfully uploaded {{ uploadResult.success_count }} file(s)</span>
      </div>
      <div class="error-message" v-if="uploadResult.error_count > 0">
        <i class="pi pi-exclamation-triangle"></i>
        <span>Failed to upload {{ uploadResult.error_count }} file(s)</span>
        <ul v-if="uploadResult.errors.length > 0">
          <li v-for="(error, index) in uploadResult.errors" :key="index">
            {{ error.filename }}: {{ error.error }}
          </li>
        </ul>
      </div>

      <div class="batch-info" v-if="uploadResult.batch_id">
        <p><strong>Batch ID:</strong> {{ uploadResult.batch_id }}</p>
        <button class="btn btn-primary" @click="processOCR">
          <i class="pi pi-bolt"></i>
          Start OCR Processing
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { uploadFiles as uploadFilesAPI, processOCR as processOCRAPI } from '@/services/uploadService'

// State
const fileInput = ref(null)
const selectedFiles = ref([])
const isDragging = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadResult = ref(null)
const splitPdfPages = ref(false)

// Computed
const hasPdfFiles = computed(() => {
  return selectedFiles.value.some(file =>
    file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
  )
})

// Emits
const emit = defineEmits(['upload-complete', 'ocr-started'])

// Methods
function triggerFileInput() {
  if (!isUploading.value) {
    fileInput.value.click()
  }
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  addFiles(files)
}

function handleDrop(event) {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  addFiles(files)
}

function addFiles(files) {
  // Filter for allowed file types
  const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/tiff']
  const validFiles = files.filter(file => {
    const isValid = allowedTypes.includes(file.type) ||
                    file.name.toLowerCase().endsWith('.pdf') ||
                    file.name.toLowerCase().endsWith('.jpg') ||
                    file.name.toLowerCase().endsWith('.jpeg') ||
                    file.name.toLowerCase().endsWith('.png') ||
                    file.name.toLowerCase().endsWith('.tiff')
    return isValid
  })

  selectedFiles.value = [...selectedFiles.value, ...validFiles]
}

function removeFile(index) {
  selectedFiles.value.splice(index, 1)
}

function clearFiles() {
  selectedFiles.value = []
  uploadResult.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function uploadFiles() {
  if (selectedFiles.value.length === 0) {
    return
  }

  isUploading.value = true
  uploadProgress.value = 0
  uploadResult.value = null

  try {
    // Create FileList-like object
    const dataTransfer = new DataTransfer()
    selectedFiles.value.forEach(file => dataTransfer.items.add(file))

    const result = await uploadFilesAPI(
      dataTransfer.files,
      (progress) => {
        uploadProgress.value = progress
      },
      splitPdfPages.value
    )

    uploadResult.value = result
    emit('upload-complete', result)

    // Clear selected files on success
    if (result.success_count > 0) {
      selectedFiles.value = []
    }

  } catch (error) {
    console.error('Upload error:', error)
    uploadResult.value = {
      success_count: 0,
      error_count: selectedFiles.value.length,
      errors: [{ filename: 'All files', error: error.message || 'Upload failed' }]
    }
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

async function processOCR() {
  if (!uploadResult.value || !uploadResult.value.submissions) {
    return
  }

  emit('ocr-started', uploadResult.value)

  // Process OCR for each submission
  for (const submission of uploadResult.value.submissions) {
    try {
      await processOCRAPI(submission.id)
    } catch (error) {
      console.error(`OCR failed for submission ${submission.id}:`, error)
    }
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.file-uploader {
  width: 100%;
}

.upload-area {
  border: 3px dashed #cbd5e0;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f7fafc;
}

.upload-area.drag-over {
  border-color: #667eea;
  background: #ebf4ff;
  transform: scale(1.02);
}

.upload-area.uploading {
  cursor: not-allowed;
  border-color: #667eea;
  background: #f7fafc;
}

.upload-prompt, .upload-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon, .progress-icon {
  font-size: 4rem;
  color: #667eea;
}

.upload-prompt h3 {
  margin: 0;
  color: #2d3748;
}

.upload-prompt p {
  margin: 0;
  color: #718096;
}

.file-types {
  font-size: 0.85rem;
  color: #a0aec0;
}

.progress-bar {
  width: 100%;
  max-width: 400px;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
}

.files-list {
  margin-top: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.files-list h4 {
  margin: 0 0 1rem 0;
  color: #2d3748;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.file-icon {
  font-size: 1.5rem;
  color: #667eea;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  font-weight: 500;
  color: #2d3748;
}

.file-size {
  font-size: 0.85rem;
  color: #718096;
}

.remove-icon {
  color: #e53e3e;
  cursor: pointer;
  padding: 0.5rem;
}

.remove-icon:hover {
  color: #c53030;
}

.upload-options {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  user-select: none;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #667eea;
}

.checkbox-label input[type="checkbox"]:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.checkbox-label span {
  color: #2d3748;
  font-size: 0.95rem;
  font-weight: 500;
}

.option-help {
  margin: 0.5rem 0 0 0;
  padding-left: 2rem;
  font-size: 0.85rem;
  color: #718096;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.option-help i {
  color: #667eea;
}

.upload-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.upload-result {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.success-message, .error-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.success-message {
  background: #c6f6d5;
  color: #22543d;
}

.success-message i {
  color: #38a169;
}

.error-message {
  background: #fed7d7;
  color: #742a2a;
}

.error-message i {
  color: #e53e3e;
}

.error-message ul {
  margin-top: 0.5rem;
  padding-left: 2rem;
}

.batch-info {
  padding: 1rem;
  background: #ebf4ff;
  border-radius: 6px;
}

.batch-info p {
  margin: 0 0 1rem 0;
}
</style>
