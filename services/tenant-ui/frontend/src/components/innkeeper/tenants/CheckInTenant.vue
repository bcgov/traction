<template>
  <div>
    <Button
      :label="t('tenants.checkIn')"
      icon="pi pi-plus"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="t('tenants.checkIn')"
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
// Other Imports
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const emit = defineEmits(['success']);

// Open popup
const displayModal = ref(false);
const openModal = async (): Promise<void> => {
  allowClose.value = true;
  displayModal.value = true;
};

// Handle the successful check in and set a flag so that we can't close without our warn-prompt button
const tenantCreated = async (): Promise<void> => {
  allowClose.value = false;
  // Propagate the success up in case anyone else needs to pay attention (even if we're not closing this yet)
  emit('success');
};
const allowClose = ref(true);
</script>
