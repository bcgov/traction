<template>
  <div>
    <Button
      :label="$t('connect.acceptInvitation.accept')"
      icon="pi pi-check"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :style="{ minWidth: '600px' }"
      :header="$t('connect.acceptInvitation.accept')"
      :modal="true"
      @update:visible="handleClose"
    >
      <AcceptInviteForm @success="$emit('success')" @closed="handleClose" />
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
import AcceptInviteForm from './AcceptInviteForm.vue';

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
