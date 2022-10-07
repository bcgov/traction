<template>
  <div>
    <Button label="Check-In Tenant" icon="pi pi-plus" @click="openModal" />
    <Dialog
      v-model:visible="displayModal"
      header="Check-In Tenant"
      :modal="true"
      :closable="allowClose"
    >
      <CheckInTenantForm
        @success="tenantCreated"
        @closed="displayModal = false"
      />
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
import CheckInTenantForm from './CheckInTenantForm.vue';

const emit = defineEmits(['success']);

// Open popup
const displayModal = ref(false);
const openModal = async () => {
  allowClose.value = true;
  displayModal.value = true;
};

// Handle the successful check in and set a flag so that we can't close without our warn-prompt button
const tenantCreated = async () => {
  allowClose.value = false;
  // Propagate the success up in case anyone else needs to pay attention (even if we're not closing this yet)
  emit('success');
};
const allowClose = ref(true);
</script>
