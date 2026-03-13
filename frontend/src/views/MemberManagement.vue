<template>
  <div class="member-management">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Member Management</h1>
        <p class="subtitle">Search, filter, and manage temple members</p>
      </div>
      <div class="header-actions">
        <button @click="handleExport" class="btn btn-outline">
          <i class="pi pi-download"></i>
          Export
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-cards" v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">Total Members</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.active }}</div>
        <div class="stat-label">Active</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.inactive }}</div>
        <div class="stat-label">Inactive</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.recent_30_days }}</div>
        <div class="stat-label">New (30 days)</div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="search-filters">
      <div class="search-box">
        <i class="pi pi-search"></i>
        <input
          v-model="searchQuery"
          @input="debouncedSearch"
          type="text"
          placeholder="Search by name, phone, or email..."
          class="search-input"
        />
        <button
          v-if="searchQuery"
          @click="clearSearch"
          class="clear-btn"
        >
          <i class="pi pi-times"></i>
        </button>
      </div>

      <div class="filters">
        <select v-model="statusFilter" @change="loadMembers" class="filter-select">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="pending">Pending</option>
          <option value="rejected">Rejected</option>
        </select>

        <select v-model="cityFilter" @change="loadMembers" class="filter-select">
          <option value="">All Cities</option>
          <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
        </select>

        <select v-model="stateFilter" @change="loadMembers" class="filter-select">
          <option value="">All States</option>
          <option v-for="state in states" :key="state" :value="state">{{ state }}</option>
        </select>

        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="btn btn-text"
        >
          <i class="pi pi-filter-slash"></i>
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Loading members...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <i class="pi pi-exclamation-triangle" style="font-size: 2rem; color: #ef4444"></i>
      <p>{{ error }}</p>
      <button @click="loadMembers" class="retry-btn">Retry</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="members.length === 0" class="empty-state">
      <i class="pi pi-users" style="font-size: 3rem; color: #9ca3af"></i>
      <h3>No members found</h3>
      <p v-if="hasActiveFilters || searchQuery">Try adjusting your search or filters</p>
      <p v-else>No members have been added yet</p>
    </div>

    <!-- Members Table -->
    <div v-else class="members-container">
      <div class="table-header">
        <span class="result-count">Showing {{ members.length }} of {{ total }} members</span>
      </div>

      <div class="members-table">
        <table>
          <thead>
            <tr>
              <th @click="sortBy('full_name')" class="sortable">
                Name
                <i v-if="sortField === 'full_name'" :class="sortIcon"></i>
              </th>
              <th>Contact</th>
              <th>Address</th>
              <th @click="sortBy('date_joined')" class="sortable">
                Joined
                <i v-if="sortField === 'date_joined'" :class="sortIcon"></i>
              </th>
              <th>Status</th>
              <th class="actions-col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="member in members"
              :key="member.id"
              @click="viewMember(member.id)"
              class="member-row"
            >
              <td class="member-name">
                <div class="name-primary">{{ member.full_name }}</div>
                <div class="name-secondary">ID: {{ member.id }}</div>
              </td>
              <td class="member-contact">
                <div v-if="member.phone_primary">
                  <i class="pi pi-phone"></i> {{ member.phone_primary }}
                </div>
                <div v-if="member.email" class="email">
                  <i class="pi pi-envelope"></i> {{ member.email }}
                </div>
              </td>
              <td class="member-address">
                <div v-if="member.city || member.state">
                  {{ member.city }}{{ member.city && member.state ? ', ' : '' }}{{ member.state }}
                </div>
                <div v-if="member.postal_code" class="address-secondary">
                  {{ member.postal_code }}
                </div>
              </td>
              <td class="member-joined">
                {{ formatDate(member.date_joined) }}
              </td>
              <td>
                <span class="status-badge" :class="`status-${member.membership_status}`">
                  {{ member.membership_status }}
                </span>
              </td>
              <td class="actions-col" @click.stop>
                <button @click="viewMember(member.id)" class="action-btn" title="View Details">
                  <i class="pi pi-eye"></i>
                </button>
                <button @click="editMember(member.id)" class="action-btn" title="Edit">
                  <i class="pi pi-pencil"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
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
          Page {{ currentPage }} of {{ totalPages }}
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

    <!-- Member Detail Modal -->
    <MemberDetailModal
      v-if="selectedMemberId"
      :member-id="selectedMemberId"
      :mode="modalMode"
      @close="selectedMemberId = null"
      @updated="handleMemberUpdated"
      @deleted="handleMemberDeleted"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getMembers,
  getMemberStats,
  getSearchSuggestions,
  exportMembers
} from '../services/memberService'
import MemberDetailModal from '../components/Members/MemberDetailModal.vue'

const router = useRouter()

// State
const loading = ref(true)
const error = ref(null)
const members = ref([])
const stats = ref(null)
const total = ref(0)
const limit = ref(50)
const offset = ref(0)

// Search and filters
const searchQuery = ref('')
const statusFilter = ref('')
const cityFilter = ref('')
const stateFilter = ref('')
const cities = ref([])
const states = ref([])

// Sorting
const sortField = ref('full_name')
const sortOrder = ref('asc')

// Selected member for detail view
const selectedMemberId = ref(null)
const modalMode = ref('view')

// Computed
const hasActiveFilters = computed(() => {
  return statusFilter.value || cityFilter.value || stateFilter.value
})

const currentPage = computed(() => Math.floor(offset.value / limit.value) + 1)
const totalPages = computed(() => Math.ceil(total.value / limit.value))

const sortIcon = computed(() => {
  return sortOrder.value === 'asc' ? 'pi pi-sort-up' : 'pi pi-sort-down'
})

// Methods
async function loadMembers() {
  loading.value = true
  error.value = null

  try {
    const params = {
      limit: limit.value,
      offset: offset.value,
      sort: sortField.value,
      order: sortOrder.value
    }

    if (searchQuery.value) params.search = searchQuery.value
    if (statusFilter.value) params.status = statusFilter.value
    if (cityFilter.value) params.city = cityFilter.value
    if (stateFilter.value) params.state = stateFilter.value

    const data = await getMembers(params)

    members.value = data.members
    total.value = data.total

  } catch (err) {
    console.error('Error loading members:', err)
    error.value = 'Failed to load members. Please try again.'
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    stats.value = await getMemberStats()
  } catch (err) {
    console.error('Error loading stats:', err)
  }
}

async function loadSuggestions() {
  try {
    const data = await getSearchSuggestions()
    cities.value = data.cities
    states.value = data.states
  } catch (err) {
    console.error('Error loading suggestions:', err)
  }
}

// Debounced search
let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    offset.value = 0  // Reset to first page
    loadMembers()
  }, 500)
}

function clearSearch() {
  searchQuery.value = ''
  loadMembers()
}

function clearFilters() {
  statusFilter.value = ''
  cityFilter.value = ''
  stateFilter.value = ''
  loadMembers()
}

function sortBy(field) {
  if (sortField.value === field) {
    // Toggle order
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
  loadMembers()
}

function previousPage() {
  if (offset.value > 0) {
    offset.value = Math.max(0, offset.value - limit.value)
    loadMembers()
  }
}

function nextPage() {
  if (offset.value + limit.value < total.value) {
    offset.value += limit.value
    loadMembers()
  }
}

function viewMember(memberId) {
  modalMode.value = 'view'
  selectedMemberId.value = memberId
}

function editMember(memberId) {
  modalMode.value = 'edit'
  selectedMemberId.value = memberId
}

function handleMemberUpdated() {
  // Reload members list and stats
  loadMembers()
  loadStats()
}

function handleMemberDeleted() {
  // Reload members list and stats after deletion
  loadMembers()
  loadStats()
}

async function handleExport() {
  try {
    const filters = {
      search: searchQuery.value,
      status: statusFilter.value,
      city: cityFilter.value,
      state: stateFilter.value
    }

    await exportMembers('excel', [], filters)
  } catch (err) {
    console.error('Error exporting members:', err)
    alert('Failed to export members. Please try again.')
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

// Load data on mount
onMounted(() => {
  loadMembers()
  loadStats()
  loadSuggestions()
})
</script>

<style scoped>
.member-management {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6b7280;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
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

.search-filters {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.search-box {
  position: relative;
  margin-bottom: 1rem;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-input {
  width: 100%;
  padding: 0.75rem 3rem 0.75rem 3rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.clear-btn {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
}

.clear-btn:hover {
  color: #4b5563;
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-select {
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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

.members-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.result-count {
  font-size: 0.875rem;
  color: #6b7280;
}

.members-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f9fafb;
}

th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e5e7eb;
}

th.sortable {
  cursor: pointer;
  user-select: none;
}

th.sortable:hover {
  background: #f3f4f6;
}

th.sortable i {
  margin-left: 0.5rem;
  font-size: 0.75rem;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.875rem;
}

.member-row {
  cursor: pointer;
  transition: background-color 0.15s;
}

.member-row:hover {
  background: #f9fafb;
}

.member-name .name-primary {
  font-weight: 500;
  color: #1f2937;
}

.member-name .name-secondary {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.member-contact div {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4b5563;
  margin-bottom: 0.25rem;
}

.member-contact .email {
  font-size: 0.8rem;
}

.member-contact i {
  color: #9ca3af;
  font-size: 0.75rem;
}

.member-address {
  color: #4b5563;
}

.member-address .address-secondary {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.member-joined {
  color: #6b7280;
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

.status-rejected {
  background: #f3f4f6;
  color: #6b7280;
  text-decoration: line-through;
}

.actions-col {
  width: 100px;
  text-align: right;
}

.action-btn {
  display: inline-flex;
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

.action-btn:hover {
  background: #f3f4f6;
  color: #667eea;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
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

.btn-text {
  background: none;
  color: #6b7280;
  padding: 0.5rem 1rem;
}

.btn-text:hover {
  color: #374151;
  background: #f3f4f6;
}
</style>
