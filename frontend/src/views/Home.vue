<template>
  <div class="home">
    <div class="welcome-card">
      <h1>Welcome to Sikh Temple Membership System</h1>
      <p class="subtitle">Process handwritten membership forms with OCR and human validation</p>

      <div class="stats-grid">
        <div class="stat-card">
          <i class="pi pi-file stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.pendingSubmissions }}</h3>
            <p>Pending Submissions</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="pi pi-check-circle stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.validatedToday }}</h3>
            <p>Validated Today</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="pi pi-users stat-icon"></i>
          <div class="stat-info">
            <h3>{{ stats.totalMembers }}</h3>
            <p>Total Members</p>
          </div>
        </div>
      </div>

      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="action-buttons">
          <router-link to="/upload" class="action-button">
            <i class="pi pi-upload"></i>
            <span>Upload New Forms</span>
          </router-link>
          <router-link to="/validation" class="action-button">
            <i class="pi pi-check-circle"></i>
            <span>Validate Forms</span>
          </router-link>
          <router-link to="/members" class="action-button">
            <i class="pi pi-users"></i>
            <span>View Members</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({
  pendingSubmissions: 0,
  validatedToday: 0,
  totalMembers: 0
})

onMounted(() => {
  // TODO: Fetch real stats from API
  stats.value = {
    pendingSubmissions: 0,
    validatedToday: 0,
    totalMembers: 0
  }
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
  color: #2d3748;
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: #718096;
  font-size: 1.1rem;
  margin: 0 0 2rem 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.9;
}

.stat-info h3 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
}

.stat-info p {
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
  opacity: 0.9;
}

.quick-actions {
  margin-top: 2rem;
}

.quick-actions h2 {
  color: #2d3748;
  margin: 0 0 1rem 0;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: white;
  border: 2px solid #667eea;
  color: #667eea;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s;
  font-weight: 600;
}

.action-button:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.action-button i {
  font-size: 1.5rem;
}
</style>
