<template>
  <aside class="app-sidebar">
    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item" active-class="active">
        <i class="pi pi-home"></i>
        <span>Home</span>
      </router-link>
      <router-link to="/upload" class="nav-item" active-class="active">
        <i class="pi pi-upload"></i>
        <span>Upload Forms</span>
      </router-link>
      <router-link to="/validation" class="nav-item" active-class="active">
        <i class="pi pi-check-circle"></i>
        <span>Validate</span>
      </router-link>
      <router-link to="/members" class="nav-item" active-class="active">
        <i class="pi pi-users"></i>
        <span>Members</span>
      </router-link>
      <router-link to="/settings" class="nav-item" active-class="active">
        <i class="pi pi-cog"></i>
        <span>Settings</span>
      </router-link>
    </nav>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 250px;
  background-color: #2d3748;
  color: white;
  padding: 1rem 0;
  box-shadow: 2px 0 4px rgba(0,0,0,0.1);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  color: #cbd5e0;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover {
  background-color: #4a5568;
  color: white;
}

.nav-item.active {
  background-color: #667eea;
  color: white;
  border-left: 4px solid #764ba2;
}

.nav-item i {
  font-size: 1.2rem;
}

.nav-item span {
  font-size: 1rem;
  font-weight: 500;
}
</style>
