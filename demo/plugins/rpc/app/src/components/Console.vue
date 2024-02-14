<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div width="100%">
    <v-toolbar flat density="compact" color="grey-darken-3">
      <v-spacer></v-spacer>
      <div class="px-3">
        <v-icon color="red" size="small">mdi-circle</v-icon>
        <v-icon color="yellow" size="small">mdi-circle</v-icon>
        <v-icon color="green" size="small">mdi-circle</v-icon>
      </div>
    </v-toolbar>
    <v-card id="shell" class="pa-3" rounded="0" elevation="0">
      <v-virtual-scroll :items="appStore.messages">
        <template v-slot:default="{ item: message }">
          <div class="pb-2">{{ message }}</div>
        </template>
      </v-virtual-scroll>
      <v-card-item class="pa-0" id="prompt">
        <template v-slot:prepend>
          <div>&rarr;</div>
        </template>
      </v-card-item>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/app'
import { watch } from 'vue'
// import { onMounted } from 'vue';
import { useGoTo } from 'vuetify'

const goTo = useGoTo()
const appStore = useAppStore()

watch(
  () => appStore.tenant,
  () => {
    if (appStore.tenant) {
      const ws = new WebSocket(`ws://localhost:8000/ws/${appStore.tenant?.walletId}`)
      ws.onopen = () => {
        appStore.addMessage('Connected to WS')
      }
      ws.onmessage = (wsMessage) => {
        const { message, topic } = JSON.parse(wsMessage.data)
        if (topic === 'rpc' || (topic === 'connections' && message.state === 'active')) {
          switch (topic) {
            case 'rpc':
              // TODO: handle rpc messages
              break
            case 'connections':
              appStore.addConnection(message)
              break
            default:
              break
          }
          appStore.addMessage(message)
        }
        goTo('#prompt', {
          container: '#shell',
          duration: 100
        })
      }
    }
  }
)
</script>

<style scoped>
#shell {
  overflow-y: auto;
  scroll-behavior: smooth;
  height: 500px;
  background-color: #616161;
  color: #fff;
}
</style>
