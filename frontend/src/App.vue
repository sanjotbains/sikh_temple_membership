<template>
  <div id="app">
    <AppHeader />
    <div class="main-container">
      <AppSidebar />
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import AppHeader from './components/common/AppHeader.vue'
import AppSidebar from './components/common/AppSidebar.vue'
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  background-color: #f5f7fa;
}
</style>
