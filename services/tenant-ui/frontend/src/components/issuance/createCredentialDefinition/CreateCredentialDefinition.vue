<template>
  <div>
    <div v-if="credDef">
      <div v-if="credDef.state && credDef.state !== 'Active'">
        <StatusChip :status="credDef.state" />
      </div>
      <div v-else>
        {{ `${credDef.cred_def_id}` }}
      </div>
    </div>
    <div v-else>
      <Button
        v-tooltip.top="'Create Credential Definition'"
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
      <CreateCredentialDefinitionForm
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

import CreateCredentialDefinitionForm from './CreateCredentialDefinitionForm.vue';

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
  displayModal.value = true;
};
const handleClose = async () => {
  displayModal.value = false;
};
</script>
