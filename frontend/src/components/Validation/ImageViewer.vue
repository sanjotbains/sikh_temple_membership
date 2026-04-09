<template>
  <div class="image-viewer">
    <div class="viewer-header">
      <h3>Form Image</h3>
      <div class="filename">{{ filename }}</div>
    </div>

    <div class="viewer-content">
      <!-- Loading overlay -->
      <div v-if="loading" class="loading-overlay">
        <i class="pi pi-spin pi-spinner"></i>
        <p>Loading image...</p>
      </div>

      <!-- Error state -->
      <div v-if="imageError && !loading" class="error">
        <i class="pi pi-exclamation-triangle"></i>
        <p>Failed to load image</p>
      </div>

      <!-- Always render the image, just hide it while loading -->
      <img
        v-show="!loading && !imageError"
        :src="imageUrl"
        :alt="filename"
        class="form-image"
        @load="onImageLoad"
        @error="onImageError"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  imageUrl: {
    type: String,
    required: true
  },
  filename: {
    type: String,
    default: 'Form Image'
  }
})

const loading = ref(true)
const imageError = ref(false)

// Debug: Log the image URL
console.log('ImageViewer - Image URL:', props.imageUrl)

function onImageLoad() {
  console.log('Image loaded successfully')
  loading.value = false
  imageError.value = false
}

function onImageError(event) {
  console.error('Image failed to load:', event)
  console.error('Image URL was:', props.imageUrl)
  loading.value = false
  imageError.value = true
}
</script>

<style scoped>
.image-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.viewer-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.viewer-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.filename {
  font-size: 0.875rem;
  color: #6b7280;
}

.viewer-content {
  flex: 1;
  overflow: auto;
  padding: 1rem;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  background: #f9fafb;
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #6b7280;
  background: #f9fafb;
  z-index: 10;
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #ef4444;
}

.form-image {
  max-width: 100%;
  height: auto;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border-radius: 4px;
  background: white;
}
</style>
