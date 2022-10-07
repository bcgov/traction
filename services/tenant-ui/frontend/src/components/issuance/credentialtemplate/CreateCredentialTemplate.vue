<template>
  <div>
    <div v-if="credentialTemplate">
      <div v-if="credentialTemplate.status === 'Active'">
        {{ `${credentialTemplate.name}:${credentialTemplate.tag}` }}
      </div>
      <div v-else>
        <StatusChip :status="credentialTemplate.status" />
      </div>
    </div>
    <div v-else>
      <Button
        v-if="schemaTemplate.status === 'Active'"
        v-tooltip.top="'Create Credential Template'"
        :disabled="!isIssuer"
        icon="pi pi-id-card"
        class="p-button-text"
        @click="openModal"
      />
    </div>
    <Dialog
      v-model:visible="displayModal"
      header="Create Credential Template"
      :modal="true"
      @update:visible="handleClose"
    >
      <CreateCredentialTemplateForm
        :schema-template-id="schemaTemplate.schema_template_id"
        @success="$emit('success')"
        @closed="handleClose"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import StatusChip from '../../common/StatusChip.vue';

import CreateCredentialTemplateForm from './CreateCredentialTemplateForm.vue';

import { useTenantStore } from '../../../store';
import { storeToRefs } from 'pinia';

const props = defineProps({
  schemaTemplate: {
    type: Object,
    required: true,
  },
});

const { isIssuer } = storeToRefs(useTenantStore());

const credentialTemplate = computed(() => {
  if (props.schemaTemplate.credential_templates.length) {
    return props.schemaTemplate.credential_templates[0];
  }
  return null;
});

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
