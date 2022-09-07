<template>
  <div>
    <Button
      :disabled="!isIssuer"
      v-tooltip.top="'Create Credential Template'"
      icon="pi pi-id-card"
      class="p-button-text"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      header="Create Credential Template"
      :modal="true"
      @update:visible="handleClose"
    >
      <CreateCredentialTemplateForm
        :schema-template-id="schemaTemplateId"
        @success="$emit('success')"
        @closed="handleClose"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';

import CreateCredentialTemplateForm from './CreateCredentialTemplateForm.vue';

import { useTenantStore } from '../../../store';
import { storeToRefs } from 'pinia';

const props = defineProps({
  schemaTemplateId: {
    type: String,
    required: true,
  },
});

const { isIssuer } = storeToRefs(useTenantStore());

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
</script>
