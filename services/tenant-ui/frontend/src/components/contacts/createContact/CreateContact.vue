<template>
  <div>
    <Button :label="t('contact.create')" icon="pi pi-plus" @click="openModal" />
    <Dialog
      v-model:visible="displayModal"
      :header=" t('contact.create')"
      :modal="true"
      @update:visible="handleClose"
    >
      <CreateContactForm @success="$emit('success')" @closed="handleClose" />
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

// Custom Components
import CreateContactForm from './CreateContactForm.vue';
// Other Imports
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

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
