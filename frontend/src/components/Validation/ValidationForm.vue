<template>
  <div class="validation-form">
    <div class="form-header">
      <h3>Member Information</h3>
      <div class="confidence-indicator">
        <span class="confidence-label">Overall Confidence:</span>
        <span class="confidence-value" :class="confidenceClass">
          {{ Math.round(overallConfidence * 100) }}%
        </span>
      </div>
    </div>

    <!-- Duplicate Warning -->
    <DuplicateWarning :duplicates="potentialDuplicates" />

    <form @submit.prevent="handleSubmit" class="form-content">
      <!-- Name Section -->
      <div class="form-section">
        <h4>Name</h4>
        <div class="form-row">
          <div class="form-field">
            <label for="first_name">First Name *</label>
            <input
              id="first_name"
              v-model="formData.first_name"
              type="text"
              required
              :class="{ 'low-confidence': getConfidence('first_name') < 0.7 }"
            />
            <ConfidenceBadge :confidence="getConfidence('first_name')" />
          </div>

          <div class="form-field">
            <label for="last_name">Last Name *</label>
            <input
              id="last_name"
              v-model="formData.last_name"
              type="text"
              required
              :class="{ 'low-confidence': getConfidence('last_name') < 0.7 }"
            />
            <ConfidenceBadge :confidence="getConfidence('last_name')" />
          </div>
        </div>

        <div class="form-field">
          <label for="full_name">Full Name</label>
          <input
            id="full_name"
            v-model="formData.full_name"
            type="text"
          />
        </div>
      </div>

      <!-- Address Section -->
      <div class="form-section">
        <div class="section-header">
          <h4>Address</h4>
          <button
            type="button"
            @click="handleValidateAddress"
            class="btn-validate-address"
            :disabled="addressValidation.validating"
          >
            <i v-if="!addressValidation.validating" class="pi pi-map-marker"></i>
            <i v-else class="pi pi-spin pi-spinner"></i>
            {{ addressValidation.validating ? 'Validating...' : 'Validate Address' }}
          </button>
        </div>

        <!-- Address Validation Result -->
        <div v-if="addressValidation.result" class="validation-result" :class="addressValidation.resultClass">
          <div class="validation-message">
            <i :class="addressValidation.resultIcon"></i>
            <span>{{ addressValidation.resultMessage }}</span>
          </div>

          <!-- Show suggestions if available -->
          <div v-if="addressValidation.result.suggestions && Object.keys(addressValidation.result.suggestions).length > 0" class="validation-suggestions">
            <p><strong>Suggested corrections:</strong></p>
            <ul>
              <li v-for="(value, field) in addressValidation.result.suggestions" :key="field">
                <strong>{{ formatFieldName(field) }}:</strong> {{ value }}
              </li>
            </ul>
            <button type="button" @click="applySuggestions" class="btn-apply-suggestions">
              <i class="pi pi-check"></i>
              Apply Suggestions
            </button>
          </div>

          <!-- Show formatted address if exact match -->
          <div v-if="addressValidation.result.is_exact_match && addressValidation.result.formatted_address" class="formatted-address">
            <strong>Verified Address:</strong> {{ addressValidation.result.formatted_address }}
          </div>
        </div>

        <div class="form-field">
          <label for="address_line1">Street Address *</label>
          <input
            id="address_line1"
            v-model="formData.address_line1"
            type="text"
            required
            :class="{ 'low-confidence': getConfidence('address_line1') < 0.7 }"
          />
          <ConfidenceBadge :confidence="getConfidence('address_line1')" />
        </div>

        <div class="form-field">
          <label for="address_line2">Address Line 2</label>
          <input
            id="address_line2"
            v-model="formData.address_line2"
            type="text"
          />
        </div>

        <div class="form-row">
          <div class="form-field">
            <label for="city">City *</label>
            <input
              id="city"
              v-model="formData.city"
              type="text"
              required
              :class="{ 'low-confidence': getConfidence('city') < 0.7 }"
            />
            <ConfidenceBadge :confidence="getConfidence('city')" />
          </div>

          <div class="form-field">
            <label for="state">State/Province *</label>
            <input
              id="state"
              v-model="formData.state"
              type="text"
              required
              :class="{ 'low-confidence': getConfidence('state') < 0.7 }"
            />
            <ConfidenceBadge :confidence="getConfidence('state')" />
          </div>

          <div class="form-field">
            <label for="postal_code">ZIP/Postal Code *</label>
            <input
              id="postal_code"
              v-model="formData.postal_code"
              type="text"
              required
              :class="{ 'low-confidence': getConfidence('postal_code') < 0.7 }"
            />
            <ConfidenceBadge :confidence="getConfidence('postal_code')" />
          </div>
        </div>
      </div>

      <!-- Contact Section -->
      <div class="form-section">
        <h4>Contact Information</h4>
        <div class="form-row">
          <div class="form-field">
            <label for="phone_primary">Phone Number *</label>
            <input
              id="phone_primary"
              v-model="formData.phone_primary"
              type="tel"
              required
              :class="{ 'low-confidence': getConfidence('phone_primary') < 0.7 }"
            />
            <ConfidenceBadge :confidence="getConfidence('phone_primary')" />
          </div>

          <div class="form-field">
            <label for="email">Email Address</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
            />
          </div>
        </div>
      </div>

      <!-- Date of Birth Section -->
      <div class="form-section">
        <h4>Date of Birth</h4>
        <div class="form-field">
          <label for="date_of_birth">Date of Birth *</label>
          <input
            id="date_of_birth"
            v-model="formData.date_of_birth"
            type="date"
            required
            :class="{ 'low-confidence': getConfidence('date_of_birth') < 0.7 }"
          />
          <ConfidenceBadge :confidence="getConfidence('date_of_birth')" />
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="form-actions">
        <button type="button" @click="handleReject" class="btn btn-danger">
          <i class="pi pi-times-circle"></i>
          Reject
        </button>
        <button type="button" @click="handleSkip" class="btn btn-secondary">
          <i class="pi pi-forward"></i>
          Skip
        </button>
        <button type="button" @click="handleSave" class="btn btn-outline">
          <i class="pi pi-save"></i>
          Save Progress
        </button>
        <button type="submit" class="btn btn-primary">
          <i class="pi pi-check"></i>
          Complete & Create Member
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import DuplicateWarning from './DuplicateWarning.vue'
import { validateAddress } from '../../services/addressValidationService'

// Props
const props = defineProps({
  extractedFields: {
    type: Object,
    required: true
  },
  submissionId: {
    type: Number,
    required: true
  },
  potentialDuplicates: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['save', 'complete', 'skip', 'reject'])

// Form data - initialize with extracted values
const formData = ref({
  first_name: '',
  last_name: '',
  full_name: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  postal_code: '',
  phone_primary: '',
  email: '',
  date_of_birth: ''
})

// Initialize form data from extracted fields
watch(() => props.extractedFields, (newFields) => {
  if (newFields) {
    Object.keys(formData.value).forEach(key => {
      const fieldData = newFields[key]
      if (fieldData && fieldData.value) {
        formData.value[key] = fieldData.value
      }
    })
  }
}, { immediate: true })

// Address validation state
const addressValidation = ref({
  validating: false,
  result: null,
  resultClass: '',
  resultIcon: '',
  resultMessage: ''
})

// Computed
const overallConfidence = computed(() => {
  return props.extractedFields?.overall_confidence || 0
})

const confidenceClass = computed(() => {
  const conf = overallConfidence.value
  if (conf >= 0.85) return 'confidence-high'
  if (conf >= 0.7) return 'confidence-medium'
  return 'confidence-low'
})

// Methods
function getConfidence(fieldName) {
  const field = props.extractedFields?.[fieldName]
  return field?.confidence || 0
}

function handleSave() {
  emit('save', formData.value)
}

function handleSubmit() {
  emit('complete', formData.value)
}

function handleSkip() {
  emit('skip')
}

function handleReject() {
  if (confirm('Are you sure you want to reject this submission? It will be marked as invalid and removed from the pending queue.')) {
    emit('reject')
  }
}

// Address validation
async function handleValidateAddress() {
  addressValidation.value.validating = true
  addressValidation.value.result = null

  try {
    const result = await validateAddress({
      address_line1: formData.value.address_line1,
      address_line2: formData.value.address_line2,
      city: formData.value.city,
      state: formData.value.state,
      postal_code: formData.value.postal_code
    })

    addressValidation.value.result = result

    if (result.is_valid) {
      if (result.is_exact_match) {
        addressValidation.value.resultClass = 'result-success'
        addressValidation.value.resultIcon = 'pi pi-check-circle'
        addressValidation.value.resultMessage = `Address verified! (${result.confidence} confidence)`
      } else {
        addressValidation.value.resultClass = 'result-warning'
        addressValidation.value.resultIcon = 'pi pi-exclamation-triangle'
        addressValidation.value.resultMessage = 'Address found with suggested corrections'
      }
    } else {
      addressValidation.value.resultClass = 'result-error'
      addressValidation.value.resultIcon = 'pi pi-times-circle'
      addressValidation.value.resultMessage = result.error || 'Address could not be validated'
    }
  } catch (error) {
    console.error('Address validation failed:', error)
    addressValidation.value.resultClass = 'result-error'
    addressValidation.value.resultIcon = 'pi pi-times-circle'
    addressValidation.value.resultMessage = 'Validation failed. Please try again.'
  } finally {
    addressValidation.value.validating = false
  }
}

function applySuggestions() {
  if (addressValidation.value.result && addressValidation.value.result.suggestions) {
    const suggestions = addressValidation.value.result.suggestions

    if (suggestions.city) {
      formData.value.city = suggestions.city
    }
    if (suggestions.state) {
      formData.value.state = suggestions.state
    }
    if (suggestions.postal_code) {
      formData.value.postal_code = suggestions.postal_code
    }

    // Clear validation result after applying suggestions
    addressValidation.value.result = null
  }
}

function formatFieldName(field) {
  const fieldNames = {
    'city': 'City',
    'state': 'State',
    'postal_code': 'Postal Code',
    'address_line1': 'Street Address'
  }
  return fieldNames[field] || field
}
</script>

<script>
// Confidence Badge Component
import { defineComponent, computed } from 'vue'

export const ConfidenceBadge = defineComponent({
  props: {
    confidence: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const badgeClass = computed(() => {
      if (props.confidence >= 0.85) return 'badge-high'
      if (props.confidence >= 0.7) return 'badge-medium'
      return 'badge-low'
    })

    const badgeText = computed(() => {
      const percentage = Math.round(props.confidence * 100)
      if (props.confidence >= 0.85) return `${percentage}% High`
      if (props.confidence >= 0.7) return `${percentage}% Medium`
      return `${percentage}% Low`
    })

    return { badgeClass, badgeText }
  },
  template: `
    <span v-if="confidence > 0" class="confidence-badge" :class="badgeClass">
      {{ badgeText }}
    </span>
  `
})
</script>

<style scoped>
.validation-form {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.form-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.confidence-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confidence-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.confidence-value {
  font-weight: 600;
  font-size: 1rem;
}

.confidence-high { color: #10b981; }
.confidence-medium { color: #f59e0b; }
.confidence-low { color: #ef4444; }

.form-content {
  flex: 1;
  overflow: auto;
  padding: 1.5rem;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.form-section:last-of-type {
  border-bottom: none;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.form-section h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.form-field {
  margin-bottom: 1rem;
  position: relative;
}

.form-field label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-field input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-field input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-field input.low-confidence {
  border-color: #fbbf24;
  background-color: #fffbeb;
}

.confidence-badge {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
  font-weight: 500;
}

.badge-high {
  background: #d1fae5;
  color: #065f46;
}

.badge-medium {
  background: #fef3c7;
  color: #92400e;
}

.badge-low {
  background: #fee2e2;
  color: #991b1b;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
  margin-top: 2rem;
}

.btn {
  display: flex;
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

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-outline {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

/* Address Validation Styles */
.btn-validate-address {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-validate-address:hover:not(:disabled) {
  background: #5568d3;
}

.btn-validate-address:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.validation-result {
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid;
}

.result-success {
  background: #d1fae5;
  border-color: #10b981;
  color: #065f46;
}

.result-warning {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
}

.result-error {
  background: #fee2e2;
  border-color: #ef4444;
  color: #991b1b;
}

.validation-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.validation-message i {
  font-size: 1.25rem;
}

.validation-suggestions {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid currentColor;
  opacity: 0.8;
}

.validation-suggestions p {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.validation-suggestions ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
  font-size: 0.875rem;
}

.validation-suggestions li {
  margin-bottom: 0.25rem;
}

.btn-apply-suggestions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  margin-top: 0.75rem;
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-apply-suggestions:hover {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

.formatted-address {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid currentColor;
  opacity: 0.8;
  font-size: 0.875rem;
}
</style>
