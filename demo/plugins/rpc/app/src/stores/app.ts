import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'

import Tenant from '@/types/tenant'

export const useAppStore = defineStore('app', () => {
  const tenant: Ref<Tenant | undefined> = ref()
  const invitation: Ref<any> = ref()
  const messages: Ref<string[]> = ref([])
  const connections: Ref<any[]> = ref([])

  function setTenant(t: Tenant) {
    tenant.value = t
  }

  function setInvitation(i: any) {
    invitation.value = i
  }

  function addMessage(message: string) {
    messages.value.push(message)
  }

  function addConnection(connection: any) {
    connections.value.push(connection)
  }

  return {
    tenant,
    invitation,
    messages,
    connections,
    setTenant,
    setInvitation,
    addMessage,
    addConnection
  }
})
