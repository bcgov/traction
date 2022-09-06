<template>
  <Button
    :label="tenant.issuer ? 'Issuer' : 'Activate Issuer'"
    :icon="tenant.issuer ? 'pi pi-check' : 'pi pi-flag'"
    class="p-button"
    :disabled="tenant.issuer"
    :loading="loading"
    @click="requestAccess"
  ></Button>
</template>

<script setup lang="ts">
import Button from 'primevue/button';
import { ref } from 'vue';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';

// For monitoring the state of the request
const loading = ref(false);

// Get the tenant store
const tenantStore = useTenantStore();

// This is the tenant state
const { tenant } = storeToRefs(tenantStore);

/**
 * Request access to the issuer
 */
const requestAccess = async () => {
  loading.value = true;
  await tenantStore.makeIssuer();
  await tenantStore.getSelf();
  loading.value = false;
};
</script>
