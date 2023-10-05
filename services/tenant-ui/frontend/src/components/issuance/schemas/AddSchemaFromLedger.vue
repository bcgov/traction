<template>
  <div>
    <Button
      :label="t('configuration.schemas.addFromLedger')"
      :disabled="!isIssuer"
      icon="pi pi-plus"
      style="margin: 0 10px"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="t('configuration.schemas.addFromLedger')"
      :modal="true"
      :style="{ minWidth: '400px' }"
      @update:visible="handleClose"
    >
      <AddSchemaFromLedgerForm
        @success="$emit('success')"
        @closed="handleClose"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
//Libraries
import { ref } from 'vue';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
// Source
import AddSchemaFromLedgerForm from './AddSchemaFromLedgerForm.vue';
import { useTenantStore } from '@/store';

const { t } = useI18n();

const { isIssuer } = storeToRefs(useTenantStore());

defineEmits(['success']);

const displayModal = ref(false);
const openModal = async () => (displayModal.value = true);
const handleClose = async () => (displayModal.value = false);
</script>
