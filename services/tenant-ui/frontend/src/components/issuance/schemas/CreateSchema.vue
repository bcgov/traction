<template>
  <div>
    <Button
      :disabled="!isIssuer"
      :label="$t('configuration.schemas.create')"
      icon="pi pi-plus"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="$t('configuration.schemas.create')"
      :modal="true"
      :style="{ minWidth: '500px' }"
    >
      <CreateSchemaForm @success="$emit('success')" @closed="handleClose" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Libraries
import { storeToRefs } from 'pinia';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
// Source
import { useGovernanceStore, useTenantStore } from '@/store';
import { SchemaSendRequest } from '@/types/acapyApi/acapyInterface';
import CreateSchemaForm from './CreateSchemaForm.vue';
import checkSchemaPostedInterval from './checkSchemaPostedInterval';

const props = defineProps({
  tableReload: {
    type: Function,
    required: false,
    default: () => {},
  },
});

defineEmits(['success']);

const { t } = useI18n();

const { isIssuer } = storeToRefs(useTenantStore());
const { selectedSchema } = storeToRefs(useGovernanceStore());
const governanceStore = useGovernanceStore();

//Modal
const displayModal = ref(false);
const openModal = async () => (displayModal.value = true);
const handleClose = async (schema: SchemaSendRequest) => {
  displayModal.value = false;
  checkSchemaPostedInterval(
    schema,
    governanceStore.getStoredSchemas,
    props.tableReload,
    t('configuration.schemas.postFinished'),
    selectedSchema
  );
};
</script>
