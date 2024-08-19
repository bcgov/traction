<template>
  <div>
    <Button
      :title="$t('tenants.settings.deleteTenant')"
      icon="pi pi-trash"
      class="p-button-rounded p-button-icon-only p-button-text"
      :disabled="props.tenant.tenant_name === 'traction_innkeeper'"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :style="{ minWidth: '500px' }"
      :header="'Delete Tenant'"
      :modal="true"
      @update:visible="handleClose"
    >
      <ConfirmTenantDeletion
        :tenant="props.tenant"
        :unsuspendable="props.unsuspendable"
        api="Innkeeper"
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

import ConfirmTenantDeletion from './ConfirmTenantDeletion.vue';

import { TenantRecord } from '@/types/acapyApi/acapyInterface';

defineEmits(['success']);

const props = defineProps<{
  tenant: TenantRecord;
  unsuspendable?: boolean;
}>();

const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
const handleClose = async () => {
  displayModal.value = false;
};
</script>
