<template>
  <div>
    <Button
      :title="$t('tenants.settings.editSettings')"
      icon="pi pi-cog"
      class="p-button-rounded p-button-icon-only p-button-text"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :style="{ minWidth: '500px' }"
      :header="$t('tenants.settings.editSettings')"
      :modal="true"
      @update:visible="handleClose"
    >
      <EditSettingsForm @success="$emit('success')" @closed="handleClose" />
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
import EditSettingsForm from './editSettingsForm.vue';

defineEmits(['success']);

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
