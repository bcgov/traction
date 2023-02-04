<template>
  <div>
    <div v-if="credDef">
      <div v-if="credDef.state === 'Active'">
        {{ `${credDef.name}:${credDef.tag}` }}
      </div>
      <div v-else>
        <StatusChip :status="credDef.state" />
      </div>
    </div>
    <div v-else>
      <Button
        v-tooltip.top="'Create Credential Template'"
        :disabled="!isIssuer"
        icon="pi pi-id-card"
        class="p-button-text"
        @click="openModal"
      />
    </div>
    <Dialog
      v-model:visible="displayModal"
      header="Create Credential Definition"
      :style="{ minWidth: '400px' }"
      :modal="true"
      @update:visible="handleClose"
    >
      <CreateCredentialTemplateForm
        :schema="schema"
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
  schema: {
    type: Object,
    required: true,
  },
});

const { isIssuer } = storeToRefs(useTenantStore());

const credDef = computed(() => {
  if (props.schema.credentialDefinition) {
    return props.schema.credentialDefinition;
  }
  return null;
});

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
