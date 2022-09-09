<template>
  <Button
    :label="label()"
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

// Other Imports
import { useToast } from 'vue-toastification';

// Notifications
const toast = useToast();

// For monitoring the state of the request
const loading = ref(false);

// Get the tenant store
const tenantStore = useTenantStore();

// This is the tenant state
const { tenant } = storeToRefs(tenantStore);

/**
 * ## requestAccess
 * Request access to the issuer
 */
const requestAccess = async () => {
  loading.value = true; // Set the spinner

  const res = await tenantStore.makeIssuer();
  if (res.issuer_status === 'N/A') {
    toast.error(
      'Sorry you do not have access yet. Please contact your Innkeeper directly.'
    );
  } else {
    await tenantStore.getSelf();
  }
  loading.value = false; // Remove the spinner
};

/**
 * ## label
 * Return the label for the button depending
 * on the state of the tenant
 */
const label = () => {
  if (tenant.value.issuer) {
    return 'Issuer';
  } else if (
    !tenant.value.issuer &&
    tenant.value.issuer_status === 'Approved'
  ) {
    return 'Approve Issuer Permissions';
  } else {
    return 'Request Issuer Permissions';
  }
};
</script>
