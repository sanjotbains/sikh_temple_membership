import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('./views/Home.vue')
    },
    {
      path: '/upload',
      name: 'upload',
      component: () => import('./views/Upload.vue')
    },
    {
      path: '/validation',
      name: 'validation',
      component: () => import('./views/ValidationDashboard.vue')
    },
    {
      path: '/validation/:id',
      name: 'validation-editor',
      component: () => import('./views/ValidationEditor.vue')
    },
    {
      path: '/members',
      name: 'members',
      component: () => import('./views/MemberManagement.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('./views/Settings.vue')
    }
  ]
})

export default router
