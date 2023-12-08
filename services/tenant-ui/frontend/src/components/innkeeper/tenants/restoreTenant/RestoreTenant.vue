<template>
  <div>
    <Button
      :title="$t('tenants.settings.restoreTenant')"
      icon="pi pi-reload"
      class="p-button-rounded p-button-icon-only p-button-text"
      :disabled="props.tenant.tenant_name === 'traction_innkeeper'"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :style="{ minWidth: '500px' }"
      :header="'Restore Tenant'"
      :modal="true"
      @update:visible="handleClose"
    >
      <ConfirmTenantRestoration
        :tenant="props.tenant"
        @success="$emit('success')"
        @closed="handleClose"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import Button from 'primevue/button';
import Dialog from 'primevue/dialog';

import ConfirmTenantRestoration from './ConfirmTenantRestoration.vue';

import { TenantRecord } from '@/types/acapyApi/acapyInterface';

defineEmits(['success']);

const props = defineProps<{
  tenant: TenantRecord;
}>();

const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
const handleClose = async () => {
  displayModal.value = false;
};
</script>
