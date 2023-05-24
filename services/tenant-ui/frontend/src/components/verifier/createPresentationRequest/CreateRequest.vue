<template>
  <div>
    <Button
      :label="$t('verify.createRequest')"
      icon="pi pi-key"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="$t('verify.createRequest')"
      :modal="true"
      :style="{ width: '600px' }"
      @update:visible="handleClose"
    >
      <CreateRequestForm @success="$emit('success')" @closed="handleClose" />
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
import CreateRequestForm from './CreateRequestForm.vue';

defineEmits(['success']);

const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
</script>
