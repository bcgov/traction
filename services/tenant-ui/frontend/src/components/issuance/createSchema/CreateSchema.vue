<template>
  <div>
    <Button
      :disabled="!isIssuer"
      label="Create Schema"
      icon="pi pi-plus"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      header="Create Schema"
      :modal="true"
      :style="{ minWidth: '500px' }"
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
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Custom Components
import CreateSchemaForm from './CreateSchemaForm.vue';

const { isIssuer } = storeToRefs(useTenantStore());

defineEmits(['success']);

// Display popup
const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs (if needed)
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
</script>
