<template>
  <div>
    <Button
      :label="$t('connect.invitation.create')"
      icon="pi pi-user-edit"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="$t('connect.invitation.create')"
      :modal="true"
      :style="{ minWidth: '400px' }"
      @update:visible="handleClose"
    >
      <CreateConnectionForm @success="$emit('success')" @closed="handleClose" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue etc
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// Custom Components
import CreateConnectionForm from './CreateConnectionForm.vue';

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
