<template>
  <!-- Make Issuer -->
  <h3 class="mt-5 mb-0">
    {{ $t('profile.issuer') }}

    <span v-if="errLoading" class="no-endorser">
      <i class="pi pi-exclamation-circle"></i>
      {{ $t('common.genericError') }}
    </span>
  </h3>

  <div v-if="writeLedger">
    <p class="my-0">
      {{ $t('profile.writeLedger', [writeLedger.ledger_id]) }}
    </p>
  </div>

  <div v-if="loadingIssuance" class="flex flex-column align-items-center">
    <ProgressSpinner />
    <p v-if="publicDidRegistrationProgress">
      {{ publicDidRegistrationProgress }}
    </p>
  </div>
  <div v-else>
    <h5 class="mb-0 mt-3">{{ $t('common.ledgers') }}</h5>
    <div v-if="endorserInfo">
      <Endorser />

      <h5 class="mb-0 mt-3">{{ $t('profile.publicDid') }}</h5>
      <PublicDid />
    </div>
    <div v-else class="no-endorser">
      <i class="pi pi-exclamation-circle"></i>
      {{ $t('profile.noEndorserInfoFound') }}
    </div>

    <h5 class="mb-0 mt-3">{{ $t('profile.taa.taaAcceptance') }}</h5>
    <TaaAcceptance />
  </div>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import ProgressSpinner from 'primevue/progressspinner';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other Components
import Endorser from './Endorser.vue';
import PublicDid from './PublicDid.vue';
import TaaAcceptance from './TaaAcceptance.vue';
import { useToast } from 'vue-toastification';

const toast = useToast();

// Get the tenant store
const tenantStore = useTenantStore();
const {
  endorserInfo,
  loadingIssuance,
  publicDidRegistrationProgress,
  writeLedger,
} = storeToRefs(tenantStore);

// Load all the issuer details
const errLoading = ref(false);
const loadIssuer = async () => {
  try {
    await Promise.all([
      tenantStore.getServerConfig(),
      tenantStore.getIssuanceStatus(),
      tenantStore.getWalletcDids(),
      tenantStore.getTransactions(),
    ]);
  } catch (error) {
    errLoading.value = true;
    toast.error(`Failure getting Issuer info: ${error}`);
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
