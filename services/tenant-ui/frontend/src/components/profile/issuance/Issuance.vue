<template>
  <!-- Make Issuer -->
  <h3 class="mt-5 mb-3">Issuer</h3>
  <div v-if="loadingIssuance" class="flex justify-content-center">
    <ProgressSpinner />
  </div>
  <div v-else>
    <h5 class="my-0">Endorser</h5>
    <div v-if="endorserInfo">
      <Endorser />

      <h5 class="mb-0 mt-3">Public DID</h5>
      <p class="my-1">Register a public DID</p>
      <InputSwitch />
    </div>
    <div v-else class="no-endorser">
      <i class="pi pi-exclamation-circle"></i>
      No Endorser info found, issuance disabled
    </div>
  </div>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, computed } from 'vue';
// PrimeVue etc
import ProgressSpinner from 'primevue/progressspinner';
import InputSwitch from 'primevue/inputswitch';
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other Components
import Endorser from '@/components/profile/issuance/Endorser.vue';

// Notifications
const toast = useToast();

// Get the tenant store
const tenantStore = useTenantStore();
const { loadingIssuance, endorserConnection, endorserInfo } =
  storeToRefs(tenantStore);

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

</script>

<style lang="scss" scoped>
.no-endorser {
  color: $tenant-ui-text-danger;
}
</style>
