<template>
  <!-- Make Issuer -->
  <h3 class="mt-5 mb-3">Issuer</h3>
  <h5 class="my-0">Endorser</h5>
  <div v-if="endorserInfo">
    Endorser Info: {{ endorserInfo }} Endorser Conn: {{ endorserConnection }}
    <br />

    <h5 class="mb-0 mt-3">Public DID</h5>
    Adding
  </div>
  <div v-else class="no-endorser">
    <i class="pi pi-exclamation-circle"></i>
    No Endorser info found, issuance disabled
  </div>
  <!-- <Issuance />  -->
  <!-- Issuer Status -->
  <!-- <div class="field mt-3">
    <label for="issStatus">Issuer Status</label>
    <InputText
      id="issStatus"
      class="w-full"
      readonly
      :value="tenant.issuer_status"
    />
  </div> -->
  <!-- <Button
    :label="label()"
    :icon="issuer ? 'pi pi-check' : 'pi pi-flag'"
    class="p-button"
    :disabled="issuer"
    :loading="loading"
    @click="requestAccess"
  ></Button> -->
</template>

<script setup lang="ts">
import Button from 'primevue/button';
import { onMounted, ref } from 'vue';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';

// Other Imports
import { useToast } from 'vue-toastification';

// Notifications
const toast = useToast();

// For monitoring the state of the request
const loading = ref(false);

// Flag for pending requests
const pending = ref(false);

// Get the tenant store
const tenantStore = useTenantStore();
const { tenant, endorserConnection, endorserInfo } = storeToRefs(tenantStore);

// Load the issuer details
const loadIssuer = async () => {
  await tenantStore.getEndorserInfo();
  if (endorserInfo) {
    await tenantStore.getEndorserConnection();
  }
};

onMounted(async () => {
  loadIssuer();
});

/**
 * Listen for changes to the tenant state
 * then adjust the appropriate ref.
 * This is the result of Pinia not being reactive with the store.
 */
// const issuer = ref(tenant.value.issuer ? true : false);
// tenantStore.$subscribe((state) => {
//   if ((state?.events as any)?.newValue?.issuer) {
//     issuer.value = (state.events as any).newValue.issuer;
//   }
// });

/**
 * ## requestAccess
 * Request access to the issuer
 */
// const requestAccess = async () => {
//   loading.value = true; // Set the spinner

//   // const res = await tenantStore.makeIssuer();
//   // if (res.issuer_status === 'N/A') {
//   //   toast.error(
//   //     'Sorry you do not have access yet. Please contact your Innkeeper directly.'
//   //   );
//   // } else {
//   //   await tenantStore.getSelf(); // Reload profile data
//   //   if (pending.value === false) {
//   //     toast.success(
//   //       'Successfully sent approval request! Check back later for status.'
//   //     );
//   //   }
//   //   pending.value = true;
//   // }
//   loading.value = false; // Remove the spinner
// };

/**
 * ## label
 * Return the label for the button depending
 * on the state of the tenant
 */
// const label = () => {
//   if (issuer.value) {
//     return 'Issuer'; // Already an issuer
//   } else if (
//     !issuer.value &&
//     tenant.value.issuer_status === 'Approved' &&
//     !pending.value
//   ) {
//     return 'Approve Issuer Permissions'; // Already approved, but not an issuer
//   } else if (pending.value) {
//     return 'Check Issuer Status'; // Requested, but not approved
//   } else {
//     return 'Request Issuer Permissions'; // Not approved yet
//   }
// };
</script>

<style lang="scss" scoped>
.no-endorser {
  color: $tenant-ui-text-danger;
}
</style>
