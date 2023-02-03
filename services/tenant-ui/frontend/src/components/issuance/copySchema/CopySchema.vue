<template>
  <div>
    <Button label="Copy Schema" icon="pi pi-copy" @click="openModal" />
    <Dialog
      v-model:visible="displayModal"
      header="Copy Schema"
      :modal="true"
      :style="{ minWidth: '400px' }"
      @update:visible="handleClose"
    >
      <CopySchemaForm @success="$emit('success')" @closed="handleClose" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// Custom Components
import CopySchemaForm from './CopySchemaForm.vue';

defineEmits(['success']);

// Open close dialog
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
