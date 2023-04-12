<template>
  <div>
    <Button
      :disabled="!isIssuer"
      label="Add/Update OCA Association"
      icon="pi pi-plus"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      header="Add/Update OCA Association"
      :modal="true"
      :style="{ minWidth: '750px', maxWidth: '750px' }"
      @update:visible="handleClose"
    >
      <CreateOcaForm @success="$emit('success')" @closed="handleClose" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { useToast } from 'vue-toastification';
// State
import { useGovernanceStore, useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Custom Components
import CreateOcaForm from './CreateOcaForm.vue';

const governanceStore = useGovernanceStore();
const { isIssuer } = storeToRefs(useTenantStore());

const toast = useToast();

defineEmits(['success']);

// Display popup
const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs in the store to fetch schemas/creds
  Promise.all([
    governanceStore.listStoredSchemas(),
    governanceStore.listStoredCredentialDefinitions(),
  ]).catch((err) => {
    console.error(err);
    toast.error(`An error occurred loading schemas or credentials: ${err}`);
  });
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
</script>
