<template>
  <div>
    <Button
      label="Create Schema"
      :disabled="!isIssuer"
      icon="pi pi-plus"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      header="Create Schema"
      :modal="true"
      @update:visible="handleClose"
    >
      <CreateSchemaForm @success="$emit('success')" @closed="handleClose" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// State
import { useTenantStore } from '../../store';

// Custom Components
import CreateSchemaForm from './CreateSchemaForm.vue';
// Other Imports
import { useToast } from 'vue-toastification';
const tenantStore = useTenantStore();
const { isIssuer } = storeToRefs(useTenantStore());

// State setup

const toast = useToast();

defineEmits(['success']);

// -----------------------------------------------------------------------
// Display popup
// ---------------------------------------------------------------------
const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs (if needed)
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
// ---------------------------------------------------------------/display
</script>
