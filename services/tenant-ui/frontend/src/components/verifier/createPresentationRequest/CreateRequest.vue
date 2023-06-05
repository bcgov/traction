<template>
  <div>
    <Button
      :title="
        iconDisplay ? $t('verify.copyRequest') : $t('verify.createRequest')
      "
      :label="$t('verify.createRequest')"
      :icon="iconDisplay ? 'pi pi-reply' : 'pi pi-key'"
      :class="
        iconDisplay ? 'p-button-rounded p-button-icon-only p-button-text' : ''
      "
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="$t('verify.createRequest')"
      :modal="true"
      :style="{ width: '600px' }"
      @update:visible="handleClose"
    >
      <CreateRequestForm
        :existing-pres-req="props.existingPresReq"
        @success="$emit('success')"
        @closed="handleClose"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Types
import { IndyProofRequest } from '@/types/acapyApi/acapyInterface';

// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// Custom Components
import CreateRequestForm from './CreateRequestForm.vue';

defineEmits(['success']);

// Props
const props = defineProps<{
  existingPresReq?: IndyProofRequest;
  iconDisplay?: boolean;
}>();

const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
</script>
