<template>
  <!-- Make Issuer -->
  <h3 class="mt-5 mb-3">Issuer</h3>
  <div v-if="loadingIssuance" class="flex flex-column align-items-center">
    <ProgressSpinner />
    <p v-if="publicDidRegistrationProgress">
      {{ publicDidRegistrationProgress }}
    </p>
  </div>
  <div v-else>
    <h5 class="my-0">Endorser</h5>
    <div v-if="endorserInfo">
      <Endorser />

      <h5 class="mb-0 mt-3">Public DID</h5>
      <PublicDid />
    </div>
    <div v-else class="no-endorser">
      <i class="pi pi-exclamation-circle"></i>
      No Endorser info found, issuance disabled
    </div>
  </div>
</template>

<script setup lang="ts">
// Vue
import { onMounted } from 'vue';
// PrimeVue
import ProgressSpinner from 'primevue/progressspinner';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other Components
import Endorser from './Endorser.vue';
import PublicDid from './PublicDid.vue';

// Get the tenant store
const tenantStore = useTenantStore();
const { loadingIssuance, endorserInfo, publicDidRegistrationProgress } =
  storeToRefs(tenantStore);

// Load the issuer details
const loadIssuer = async () => {
  await tenantStore.getEndorserInfo();
  if (endorserInfo) {
    await Promise.all([
      tenantStore.getEndorserConnection(),
      tenantStore.getPublicDid(),
    ]);
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
