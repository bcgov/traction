<template>
  <div>
    <Button
      :disabled="isOfferButtonDisabled"
      :label="$t('issue.offer')"
      icon="pi pi-arrow-up-right"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="$t('issue.offer')"
      :modal="true"
      :style="{ width: '500px' }"
      @update:visible="handleClose"
    >
      <OfferCredentialForm @success="$emit('success')" @closed="handleClose" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { computed, onMounted, ref, watch } from 'vue';
// PrimeVue/ etc
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { useToast } from 'vue-toastification';
// State
import {
  useConnectionStore,
  useGovernanceStore,
  useTenantStore,
} from '@/store';
import { storeToRefs } from 'pinia';
import { API_PATH } from '@/helpers/constants';
import { useAcapyApi } from '@/store/acapyApi';
// Custom Components
import OfferCredentialForm from './OfferCredentialForm.vue';

// State setup
const connectionStore = useConnectionStore();
const governanceStore = useGovernanceStore();

const toast = useToast();
const acapyApi = useAcapyApi();

const { isIssuer, tenantWallet } = storeToRefs(useTenantStore());

// Check if wallet is askar-anoncreds
const isAskarAnoncredsWallet = computed(() => {
  if (!tenantWallet) return false;
  return tenantWallet.value?.settings?.['wallet.type'] === 'askar-anoncreds';
});

// WebVH configuration state
const webvhConfig = ref<any>(null);
const webvhConfigLoaded = ref(false);

// Check if webvh endorser is connected
const isWebvhEndorserConnected = computed(() => {
  if (!isAskarAnoncredsWallet.value) {
    return true; // For non-askar-anoncreds wallets, always allow
  }

  if (!webvhConfig.value) {
    return false;
  }

  const witnesses = webvhConfig.value.witnesses;
  return Boolean(witnesses && Array.isArray(witnesses) && witnesses.length > 0);
});

// Disable button logic:
// - For askar wallets: require isIssuer to be true
// - For askar-anoncreds wallets: only require WebVH endorser to be connected
const isOfferButtonDisabled = computed(() => {
  if (isAskarAnoncredsWallet.value) {
    return !isWebvhEndorserConnected.value;
  } else {
    return !isIssuer?.value;
  }
});

// Load webvh configuration
const loadWebvhConfig = async () => {
  if (!isAskarAnoncredsWallet.value) {
    webvhConfigLoaded.value = true;
    return;
  }

  try {
    const response = await acapyApi.getHttp(API_PATH.DID_WEBVH_CONFIG);
    const configData = response?.data ?? response ?? null;
    const isEmptyConfig =
      !configData ||
      (typeof configData === 'object' && Object.keys(configData).length === 0);
    webvhConfig.value = isEmptyConfig ? null : configData;
  } catch (_error) {
    webvhConfig.value = null;
  } finally {
    webvhConfigLoaded.value = true;
  }
};

onMounted(() => {
  loadWebvhConfig();
});

// Also reload config when wallet type changes
watch(
  () => isAskarAnoncredsWallet.value,
  (isAnoncreds) => {
    if (isAnoncreds) {
      webvhConfigLoaded.value = false;
      loadWebvhConfig();
    }
  }
);

defineEmits(['success']);

// Display popup and load needed lists
const displayModal = ref(false);
const openModal = async () => {
  // Check wallet type to determine which endpoints to use
  const walletType = tenantWallet?.value?.settings?.['wallet.type'];
  const isAskarAnoncreds = walletType === 'askar-anoncreds';

  // Kick of the loading asyncs in the store to fetch connections/creds
  // Load them in parallel but don't use Promise.all since they return different types
  const loadPromises: Promise<any>[] = [connectionStore.listConnections()];

  if (isAskarAnoncreds) {
    // For askar-anoncreds wallets, use AnonCreds endpoints
    loadPromises.push(
      governanceStore.listAnoncredsSchemas(),
      governanceStore.listAnoncredsCredentialDefinitions()
    );
  } else {
    // For askar wallets, use regular endpoints
    loadPromises.push(
      governanceStore.listStoredSchemas(),
      governanceStore.listStoredCredentialDefinitions()
    );
  }

  Promise.all(loadPromises).catch((err) => {
    console.error(err);
    toast.error(
      `An error occurred loading your connections or credentials: ${err}`
    );
  });
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
</script>
