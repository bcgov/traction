<template>
  <div>
    <Button
      :disabled="!isIssuer"
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
import { onMounted, ref, watch } from 'vue';
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
// Custom Components
import OfferCredentialForm from './OfferCredentialForm.vue';

// State setup
const connectionStore = useConnectionStore();
const governanceStore = useGovernanceStore();

const toast = useToast();

const tenantStore = useTenantStore();
const { isIssuer, isAskarAnoncredsWallet } = storeToRefs(tenantStore);

onMounted(() => {
  // Load webvh config if using askar-anoncreds wallet
  if (isAskarAnoncredsWallet?.value) {
    tenantStore.getWebvhConfig();
  }
});

// Also reload config when wallet type changes
watch(
  () => isAskarAnoncredsWallet?.value,
  (isAnoncreds) => {
    if (isAnoncreds) {
      tenantStore.getWebvhConfig();
    }
  }
);

defineEmits(['success']);

// Display popup and load needed lists
const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs in the store to fetch connections/creds
  // Load them in parallel but don't use Promise.all since they return different types
  const loadPromises: Promise<any>[] = [connectionStore.listConnections()];

  // For both wallet types, use schema and credential definition storage (anoncreds are now automatically stored)
  loadPromises.push(
    governanceStore.listStoredSchemas(),
    governanceStore.listStoredCredentialDefinitions()
  );

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
