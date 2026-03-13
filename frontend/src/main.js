import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import App from './App.vue'
import router from './router'

// PrimeVue CSS
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'

// App CSS
import './assets/styles/main.css'

// Create app
const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)
app.use(PrimeVue)

// Mount app
app.mount('#app')
