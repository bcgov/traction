import './assets/main.css'
import '@mdi/font/css/materialdesignicons.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { mdi, aliases } from 'vuetify/iconsets/mdi'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import AgentService from '@/services/agent'
import ConnectionService from '@/services/connection'
import DrpcService from '@/services/drpc'

import App from '@/App.vue'

const app = createApp(App)

app.use(createPinia())
app.use(
  createVuetify({
    components,
    directives,
    icons: {
      defaultSet: 'mdi',
      aliases,
      sets: {
        mdi
      }
    }
  })
)

const agentService = new AgentService()
const connectionService = new ConnectionService(agentService)
const drpcService = new DrpcService(agentService)

// Provide services here
app.provide('agentService', agentService)
app.provide('connectionService', connectionService)
app.provide('drpcService', drpcService)

app.mount('#app')
