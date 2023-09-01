<template>
  <div>
    <Button
      :label="$t('apiKey.createApiKey')"
      icon="pi pi-plus"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :style="{ minWidth: '600px' }"
      :header="$t('apiKey.createApiKey')"
      :modal="true"
      @update:visible="handleClose"
    >
      <CreateApiKeyForm @success="$emit('success')" @closed="handleClose" />
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
import CreateApiKeyForm from './CreateApiKeyForm.vue';
// Other Imports

defineEmits(['success']);

const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
const handleClose = async () => {
  displayModal.value = false;
};
</script>
