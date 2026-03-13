<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <!-- Header -->
      <div class="modal-header">
        <h2>{{ isEditing ? 'Edit Member' : 'Member Details' }}</h2>
        <button @click="closeModal" class="close-btn">
          <i class="pi pi-times"></i>
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="modal-body loading">
        <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
        <p>Loading member details...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="modal-body error">
        <i class="pi pi-exclamation-triangle" style="font-size: 2rem; color: #ef4444"></i>
        <p>{{ error }}</p>
        <button @click="loadMember" class="btn btn-primary">Retry</button>
      </div>

      <!-- Content -->
      <div v-else class="modal-body">
        <div class="member-info">
          <!-- Name Section -->
          <div class="info-section">
            <h3>Personal Information</h3>
            <div class="info-grid">
              <div class="info-item">
                <label>Full Name</label>
                <input
                  v-if="isEditing"
                  v-model="editForm.full_name"
                  type="text"
                  class="form-input"
                  placeholder="Enter full name"
                />
                <div v-else class="info-value">{{ member.full_name }}</div>
              </div>
              <div class="info-item">
                <label>Date of Birth</label>
                <input
                  v-if="isEditing"
                  v-model="editForm.date_of_birth"
                  type="date"
                  class="form-input"
                />
                <div v-else class="info-value">{{ formatDate(member.date_of_birth) }}</div>
              </div>
            </div>
          </div>

          <!-- Contact Section -->
          <div class="info-section">
            <h3>Contact Information</h3>
            <div class="info-grid">
              <div class="info-item">
                <label>Primary Phone</label>
                <input
                  v-if="isEditing"
                  v-model="editForm.phone_primary"
                  type="tel"
                  class="form-input"
                  placeholder="Primary phone"
                />
                <div v-else class="info-value">{{ member.phone_primary || 'N/A' }}</div>
              </div>
              <div class="info-item">
                <label>Secondary Phone</label>
                <input
                  v-if="isEditing"
                  v-model="editForm.phone_secondary"
                  type="tel"
                  class="form-input"
                  placeholder="Secondary phone"
                />
                <div v-else class="info-value">{{ member.phone_secondary || 'N/A' }}</div>
              </div>
              <div class="info-item full-width">
                <label>Email</label>
                <input
                  v-if="isEditing"
                  v-model="editForm.email"
                  type="email"
                  class="form-input"
                  placeholder="Email address"
                />
                <div v-else class="info-value">{{ member.email || 'N/A' }}</div>
              </div>
            </div>
          </div>

          <!-- Address Section -->
          <div class="info-section">
            <h3>Address</h3>
            <div v-if="isEditing" class="info-grid">
              <div class="info-item full-width">
                <label>Address Line 1</label>
                <input
                  v-model="editForm.address_line1"
                  type="text"
                  class="form-input"
                  placeholder="Street address"
                />
              </div>
              <div class="info-item full-width">
                <label>Address Line 2</label>
                <input
                  v-model="editForm.address_line2"
                  type="text"
                  class="form-input"
                  placeholder="Apt, suite, etc."
                />
              </div>
              <div class="info-item">
                <label>City</label>
                <input
                  v-model="editForm.city"
                  type="text"
                  class="form-input"
                  placeholder="City"
                />
              </div>
              <div class="info-item">
                <label>State</label>
                <input
                  v-model="editForm.state"
                  type="text"
                  class="form-input"
                  placeholder="State"
                />
              </div>
              <div class="info-item">
                <label>Postal Code</label>
                <input
                  v-model="editForm.postal_code"
                  type="text"
                  class="form-input"
                  placeholder="Postal code"
                />
              </div>
              <div class="info-item">
                <label>Country</label>
                <input
                  v-model="editForm.country"
                  type="text"
                  class="form-input"
                  placeholder="Country"
                />
              </div>
            </div>
            <div v-else class="address-block">
              <div v-if="member.address_line1">{{ member.address_line1 }}</div>
              <div v-if="member.address_line2">{{ member.address_line2 }}</div>
              <div v-if="member.city || member.state || member.postal_code">
                {{ member.city }}{{ member.city && member.state ? ', ' : '' }}{{ member.state }} {{ member.postal_code }}
              </div>
              <div v-if="member.country">{{ member.country }}</div>
              <div v-if="!member.address_line1 && !member.city" class="no-data">No address provided</div>
            </div>
          </div>

          <!-- Membership Section -->
          <div class="info-section">
            <h3>Membership</h3>
            <div class="info-grid">
              <div class="info-item">
                <label>Member ID</label>
                <div class="info-value">#{{ member.id }}</div>
              </div>
              <div class="info-item">
                <label>Date Joined</label>
                <div class="info-value">{{ formatDate(member.date_joined) }}</div>
              </div>
              <div class="info-item">
                <label>Status</label>
                <select
                  v-if="isEditing"
                  v-model="editForm.membership_status"
                  class="form-input"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="pending">Pending</option>
                </select>
                <div v-else>
                  <span class="status-badge" :class="`status-${member.membership_status}`">
                    {{ member.membership_status }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Notes Section -->
          <div v-if="member.notes || isEditing" class="info-section">
            <h3>Notes</h3>
            <textarea
              v-if="isEditing"
              v-model="editForm.notes"
              class="form-textarea"
              placeholder="Add notes about this member"
              rows="4"
            ></textarea>
            <div v-else class="notes-content">{{ member.notes }}</div>
          </div>

          <!-- Submissions Section -->
          <div v-if="member.submissions && member.submissions.length > 0" class="info-section">
            <h3>Form Submissions</h3>
            <div class="submissions-list">
              <div v-for="submission in member.submissions" :key="submission.id" class="submission-item">
                <i class="pi pi-file"></i>
                <a
                  href="#"
                  @click.prevent="openSubmissionImages(submission)"
                  class="submission-link"
                  :title="`Click to view ${submission.images?.length || 0} image(s)`"
                >
                  {{ submission.file_name }}
                  <i class="pi pi-external-link"></i>
                </a>
                <span class="submission-date">{{ formatDate(submission.uploaded_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer" v-if="!loading && !error">
        <div class="footer-left">
          <button
            v-if="!isEditing"
            @click="handleDelete"
            class="btn btn-danger-outline"
            :disabled="saving"
          >
            <i class="pi pi-trash"></i>
            Delete Member
          </button>
        </div>
        <div class="footer-right">
          <template v-if="isEditing">
            <button @click="cancelEdit" class="btn btn-outline" :disabled="saving">
              Cancel
            </button>
            <button @click="saveMember" class="btn btn-primary" :disabled="saving">
              <i v-if="saving" class="pi pi-spin pi-spinner"></i>
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </template>
          <button v-else @click="closeModal" class="btn btn-outline">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getMember, updateMember, rejectMember } from '../../services/memberService'
import { getImageUrl } from '../../services/validationService'

const props = defineProps({
  memberId: {
    type: Number,
    required: true
  },
  mode: {
    type: String,
    default: 'view',
    validator: (value) => ['view', 'edit'].includes(value)
  }
})

const emit = defineEmits(['close', 'updated', 'deleted'])

// State
const loading = ref(true)
const error = ref(null)
const member = ref(null)
const isEditing = ref(false)
const editForm = ref(null)
const saving = ref(false)

// Methods
async function loadMember() {
  loading.value = true
  error.value = null

  try {
    const data = await getMember(props.memberId)
    member.value = data.member
    // Initialize edit form with member data
    initializeEditForm()
  } catch (err) {
    console.error('Error loading member:', err)
    error.value = 'Failed to load member details. Please try again.'
  } finally {
    loading.value = false
  }
}

function initializeEditForm() {
  if (member.value) {
    editForm.value = {
      full_name: member.value.full_name || '',
      date_of_birth: member.value.date_of_birth || '',
      phone_primary: member.value.phone_primary || '',
      phone_secondary: member.value.phone_secondary || '',
      email: member.value.email || '',
      address_line1: member.value.address_line1 || '',
      address_line2: member.value.address_line2 || '',
      city: member.value.city || '',
      state: member.value.state || '',
      postal_code: member.value.postal_code || '',
      country: member.value.country || '',
      membership_status: member.value.membership_status || 'active',
      notes: member.value.notes || ''
    }
  }
}

async function saveMember() {
  if (!editForm.value) return

  saving.value = true
  error.value = null

  try {
    await updateMember(props.memberId, editForm.value)
    // Reload member data
    await loadMember()
    isEditing.value = false
    emit('updated')
  } catch (err) {
    console.error('Error updating member:', err)
    error.value = 'Failed to update member. Please try again.'
  } finally {
    saving.value = false
  }
}

function cancelEdit() {
  initializeEditForm()
  isEditing.value = false
}

async function handleDelete() {
  const confirmed = confirm(
    'Are you sure you want to delete this member?\n\n' +
    'This will:\n' +
    '- Mark the member as rejected\n' +
    '- Mark all associated submissions as rejected\n' +
    '- Remove them from the active members list\n\n' +
    'This action cannot be undone.'
  )

  if (!confirmed) return

  // Optionally ask for a reason
  const reason = prompt('Please provide a reason for deletion (optional):')

  saving.value = true
  error.value = null

  try {
    await rejectMember(props.memberId, reason || '')
    emit('deleted')
    emit('close')
  } catch (err) {
    console.error('Error deleting member:', err)
    error.value = 'Failed to delete member. Please try again.'
  } finally {
    saving.value = false
  }
}

function closeModal() {
  emit('close')
}

function openSubmissionImages(submission) {
  // If submission has images, open them in new tabs
  if (submission.images && submission.images.length > 0) {
    // Open each image in a new tab
    submission.images.forEach((image, index) => {
      const imageUrl = getImageUrl(submission.id, image.id)
      // Add a small delay between opening tabs to prevent browser blocking
      setTimeout(() => {
        window.open(imageUrl, '_blank')
      }, index * 100)
    })
  } else {
    alert('No images available for this submission')
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

// Load on mount
onMounted(() => {
  loadMember()
  isEditing.value = props.mode === 'edit'
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.modal-body.loading,
.modal-body.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 4rem 2rem;
}

.info-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.info-section:last-child {
  border-bottom: none;
}

.info-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.info-value {
  font-size: 0.875rem;
  color: #1f2937;
}

.address-block {
  font-size: 0.875rem;
  color: #1f2937;
  line-height: 1.5;
}

.address-block div {
  margin-bottom: 0.25rem;
}

.no-data {
  color: #9ca3af;
  font-style: italic;
}

.notes-content {
  font-size: 0.875rem;
  color: #4b5563;
  line-height: 1.6;
  white-space: pre-wrap;
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.submission-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
  font-size: 0.875rem;
}

.submission-item i.pi-file {
  color: #667eea;
  flex-shrink: 0;
}

.submission-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s;
  cursor: pointer;
}

.submission-link:hover {
  color: #5568d3;
  text-decoration: underline;
}

.submission-link i {
  font-size: 0.75rem;
  opacity: 0.7;
}

.submission-date {
  margin-left: auto;
  color: #6b7280;
  font-size: 0.8125rem;
  flex-shrink: 0;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
}

.status-inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.footer-left {
  display: flex;
  gap: 0.5rem;
}

.footer-right {
  display: flex;
  gap: 0.5rem;
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
}

.btn-primary {
  background: #667eea;
  color: white;
  border: none;
}

.btn-primary:hover {
  background: #5568d3;
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

.btn-danger-outline {
  background: white;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.btn-danger-outline:hover {
  background: #fef2f2;
  border-color: #dc2626;
  color: #dc2626;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1f2937;
  transition: all 0.15s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
  line-height: 1.5;
}
</style>
