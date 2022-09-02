<template>
  <div>
    <Button label="Create Contact" icon="pi pi-plus" @click="openModal" />
    <Dialog
      v-model:visible="displayModal"
      header="Create Contact"
      :modal="true"
    >
      <CreateContactForm @closed="displayModal = false" />
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
import { useToast } from 'vue-toastification';

// State setup

const toast = useToast();

// -----------------------------------------------------------------------
// Display popup
// ---------------------------------------------------------------------
const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs (if needed)
  displayModal.value = true;
};
// ---------------------------------------------------------------/display
</script>
