<template>
  <div>
    <Button label="Accept Invitation" icon="pi pi-plus" @click="openModal" />
    <Dialog
      v-model:visible="displayModal"
      header="Accept Invitation"
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
// State

// Custom Components
import AcceptInviteForm from './AcceptInviteForm.vue';
// Other Imports
import { useToast } from 'vue-toastification';

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
