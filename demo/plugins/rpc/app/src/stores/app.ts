import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'

import Tenant from '@/types/tenant';

export const useAppStore = defineStore('app', () => {
  const tenant: Ref<Tenant | undefined> = ref()
  const invitation: Ref<any> = ref()

  function setTenant(t: Tenant) {
    tenant.value = t;
  }

  function setInvitation(i: any) {
    invitation.value = i;
  }

  return { tenant, setTenant, invitation, setInvitation }
})
