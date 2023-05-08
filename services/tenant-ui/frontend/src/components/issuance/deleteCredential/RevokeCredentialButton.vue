<template>
  <Button
    v-if="canRevoke"
    :title="$t('issue.revoke.revokeCred')"
    icon="pi pi-times-circle"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="openModal"
  />
  <Dialog
    v-model:visible="displayModal"
    :style="{ width: '500px' }"
    :header="$t('issue.revoke.revokeCred')"
    :modal="true"
    @update:visible="handleClose"
  >
    <RevokeCredentialForm
      :connection-display="props.connectionDisplay"
      :cred-exch-record="props.credExchRecord"
      @success="$emit('success')"
      @closed="handleClose"
    />
  </Dialog>
</template>

<script setup lang="ts">
// Types
import { V10CredentialExchange } from '@/types/acapyApi/acapyInterface';

// Vue/State
import { computed, ref } from 'vue';
// PrimeVue/etc
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// Components
import RevokeCredentialForm from './RevokeCredentialForm.vue';

defineEmits(['success']);

// Props
const props = defineProps<{
  credExchRecord: V10CredentialExchange;
  connectionDisplay: string;
}>();

// Check revocation allowed
const canRevoke = computed(() => {
  return (
    props.credExchRecord.state === 'credential_acked' &&
    props.credExchRecord.revocation_id &&
    props.credExchRecord.revoc_reg_id
  );
});

// Display form
const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
const handleClose = async () => {
  displayModal.value = false;
};
</script>
