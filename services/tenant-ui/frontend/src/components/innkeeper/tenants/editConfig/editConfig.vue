<template>
  <div>
    <Button
      :title="$t('tenants.settings.editSettings')"
      icon="pi pi-cog"
      class="p-button-rounded p-button-icon-only p-button-text"
      :disabled="props.tenant.tenant_name === 'traction_innkeeper'"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :style="{ minWidth: '500px' }"
      :header="$t('tenants.settings.editSettings')"
      :modal="true"
      @update:visible="handleClose"
    >
      <EditConfigForm
        :tenant="props.tenant"
        @success="$emit('success')"
        @closed="handleClose"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Types
import { TenantRecord } from '@/types/acapyApi/acapyInterface';

// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// Custom Components
import EditConfigForm from './editConfigForm.vue';

defineEmits(['success']);

// Props
const props = defineProps<{
  tenant: TenantRecord;
}>();

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
