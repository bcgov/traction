<template>
  <div>
    <Button
      v-if="props.iconButton"
      v-tooltip.top="'Create Credential Template'"
      icon="pi pi-id-card"
      class="p-button-text"
      @click="openModal"
    />
    <Button
      v-else
      label="Create Credential Template"
      icon="pi pi-id-card"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      header="Create Credential Template"
      :modal="true"
    >
      <CreateCredentialTemplateForm :schema-template-id="schemaTemplateId" />
    </Dialog>
  </div>
</template>
<script setup lang="ts">
import { PropType, ref } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';

import CreateCredentialTemplateForm from './CreateCredentialTemplateForm.vue';

const props = defineProps({
  iconButton: {
    type: Boolean,
    required: false,
    default: true,
  },
  schemaTemplateId: {
    type: String,
    required: true,
  },
});

// -----------------------------------------------------------------------
// Display popup
// ---------------------------------------------------------------------
const displayModal = ref(false);
const openModal = async () => {
  // this is where you would do any async loading if you needed it for
  // your display component
  displayModal.value = true;
};
// ---------------------------------------------------------------/display
</script>
