<template>
  <v-container fluid class="px-0 py-2">
    <v-row no-gutters>
      <v-col cols="4">
        <aside>
          <Navigator class="px-2" />
        </aside>
      </v-col>
      <v-col>
        <main>
          <Console class="px-2" />
        </main>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import Navigator from '@/components/Navigator.vue'
import Console from '@/components/Console.vue'
import AgentService from '@/services/agent'
import { useAppStore } from '@/stores/app'
import { inject, onBeforeMount } from 'vue'

// Inject the agent service using the composition API
const agentService: AgentService | undefined = inject('agentService')

const appStore = useAppStore()

onBeforeMount(async () => {
  const tenant = await agentService?.fetchTenant()
  if (tenant) {
    appStore.setTenant(tenant)
  }
})
</script>

<style scoped></style>
