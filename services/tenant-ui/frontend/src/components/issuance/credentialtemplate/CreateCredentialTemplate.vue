<template>
  <Button
    v-tooltip.top="'Create Credential Template'"
    icon="pi pi-id-card"
    class="p-button-text"
    @click="displayForm = true"
  />
  <Dialog
    v-model:visible="displayForm"
    header="Create Credential Template"
    :modal="true"
  >
    <CreateCredentialTemplateForm :schema-template-id="schemaTemplateId" />
  </Dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';

import CreateCredentialTemplateForm from './CreateCredentialTemplateForm.vue';

const props = defineProps({
  schemaTemplateId: {
    type: String,
    required: true,
  },
});

const displayForm = ref(false);
</script>
