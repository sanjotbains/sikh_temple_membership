<template>
  <header class="app-header">
    <div class="header-content">
      <div class="logo-section">
        <h1>Sikh Temple Membership System</h1>
      </div>
      <div class="header-actions">
        <span class="status-indicator">
          <i class="pi pi-circle-fill" :class="statusClass"></i>
          {{ connectionStatus }}
        </span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'

const isConnected = ref(true)

const connectionStatus = computed(() => isConnected.value ? 'Connected' : 'Disconnected')
const statusClass = computed(() => isConnected.value ? 'status-online' : 'status-offline')
</script>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.status-online {
  color: #10b981;
}

.status-offline {
  color: #ef4444;
}
</style>
