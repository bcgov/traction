<template>
  <Button
    :label="label()"
    :icon="issuer ? 'pi pi-check' : 'pi pi-flag'"
    class="p-button"
    :disabled="issuer"
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
const { tenant } = storeToRefs(tenantStore); // This isn't updating

/**
 * Listen for changes to the tenant state
 * then adjust the appropriate ref.
 * This is the result of Pinia not being reactive with the store.
 */
const issuer = ref(tenant.value.issuer ? true : false);
tenantStore.$subscribe((state) => {
  if ((state?.events as any)?.newValue?.issuer) {
    issuer.value = (state.events as any).newValue.issuer;
  }
});

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
    await tenantStore.getSelf(); // Reload profile data
    toast.success('You are now an issuer!');
  }
  loading.value = false; // Remove the spinner
};

/**
 * ## label
 * Return the label for the button depending
 * on the state of the tenant
 */
const label = () => {
  if (issuer.value) {
    return 'Issuer';
  } else if (!issuer.value && tenant.value.issuer_status === 'Approved') {
    return 'Approve Issuer Permissions';
  } else {
    return 'Request Issuer Permissions';
  }
};
</script>
