<template>
  <div v-if="duplicates && duplicates.length > 0" class="duplicate-warning">
    <div class="warning-header">
      <i class="pi pi-exclamation-triangle"></i>
      <h3>Potential Duplicates Found</h3>
    </div>

    <p class="warning-message">
      This submission may be a duplicate of {{ duplicates.length }} existing {{ duplicates.length === 1 ? 'member' : 'members' }}.
      Please review carefully before creating a new member.
    </p>

    <div class="duplicate-list">
      <div
        v-for="duplicate in duplicates"
        :key="duplicate.member.id"
        class="duplicate-item"
        :class="{ 'high-confidence': duplicate.similarity_score >= 90 }"
      >
        <div class="duplicate-header">
          <div class="member-info">
            <span class="member-name">{{ duplicate.member.full_name }}</span>
            <span class="member-id">ID: #{{ duplicate.member.id }}</span>
          </div>
          <div class="similarity-score" :class="getScoreClass(duplicate.similarity_score)">
            {{ duplicate.similarity_score }}% Match
          </div>
        </div>

        <div class="match-details">
          <div class="matched-fields">
            <strong>Matched Fields:</strong>
            <div class="field-badges">
              <span
                v-for="field in duplicate.match_fields.matched_fields"
                :key="field"
                class="field-badge"
              >
                {{ formatFieldName(field) }}
              </span>
              <span v-if="duplicate.match_fields.matched_fields.length === 0" class="no-fields">
                No exact matches
              </span>
            </div>
          </div>

          <div class="member-details">
            <div class="detail-row" v-if="duplicate.member.phone_primary">
              <i class="pi pi-phone"></i>
              <span>{{ duplicate.member.phone_primary }}</span>
            </div>
            <div class="detail-row" v-if="duplicate.member.email">
              <i class="pi pi-envelope"></i>
              <span>{{ duplicate.member.email }}</span>
            </div>
            <div class="detail-row" v-if="duplicate.member.address_line1">
              <i class="pi pi-map-marker"></i>
              <span>
                {{ duplicate.member.address_line1 }}
                <span v-if="duplicate.member.city">, {{ duplicate.member.city }}</span>
                <span v-if="duplicate.member.state">, {{ duplicate.member.state }}</span>
              </span>
            </div>
            <div class="detail-row" v-if="duplicate.member.date_of_birth">
              <i class="pi pi-calendar"></i>
              <span>DOB: {{ formatDate(duplicate.member.date_of_birth) }}</span>
            </div>
          </div>

          <button @click="viewMember(duplicate.member.id)" class="btn-view-member">
            <i class="pi pi-eye"></i>
            View Full Profile
          </button>
        </div>
      </div>
    </div>

    <div class="warning-actions">
      <p class="action-note">
        <i class="pi pi-info-circle"></i>
        If this is a duplicate, you should skip this submission or merge it with an existing member.
      </p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  duplicates: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['view-member'])

function getScoreClass(score) {
  if (score >= 90) return 'score-high'
  if (score >= 70) return 'score-medium'
  return 'score-low'
}

function formatFieldName(field) {
  const names = {
    'name': 'Name',
    'phone': 'Phone',
    'email': 'Email',
    'address': 'Address',
    'dob': 'Date of Birth'
  }
  return names[field] || field
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

function viewMember(memberId) {
  emit('view-member', memberId)
}
</script>

<style scoped>
.duplicate-warning {
  background: #fef3c7;
  border: 2px solid #f59e0b;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.warning-header i {
  color: #f59e0b;
  font-size: 1.5rem;
}

.warning-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #92400e;
  margin: 0;
}

.warning-message {
  color: #92400e;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.duplicate-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.duplicate-item {
  background: white;
  border: 1px solid #fbbf24;
  border-radius: 6px;
  padding: 1rem;
}

.duplicate-item.high-confidence {
  border-color: #ef4444;
  border-width: 2px;
}

.duplicate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #fef3c7;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.member-name {
  font-weight: 600;
  font-size: 1rem;
  color: #1f2937;
}

.member-id {
  font-size: 0.875rem;
  color: #6b7280;
}

.similarity-score {
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.875rem;
}

.score-high {
  background: #fee2e2;
  color: #991b1b;
}

.score-medium {
  background: #fed7aa;
  color: #92400e;
}

.score-low {
  background: #fef3c7;
  color: #92400e;
}

.match-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.matched-fields strong {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.field-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.field-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.no-fields {
  font-size: 0.875rem;
  color: #9ca3af;
  font-style: italic;
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #4b5563;
}

.detail-row i {
  color: #9ca3af;
  width: 1rem;
}

.btn-view-member {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #4b5563;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-view-member:hover {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

.warning-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #fbbf24;
}

.action-note {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #92400e;
  margin: 0;
}

.action-note i {
  color: #f59e0b;
}
</style>
