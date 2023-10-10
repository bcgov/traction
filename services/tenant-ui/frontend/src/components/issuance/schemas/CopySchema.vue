<template>
  <Button
    :disabled="!isIssuer"
    :title="t('configuration.schemas.copy')"
    icon="pi pi-copy"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="openModal(storedSchema)"
  />
  <Dialog
    v-model:visible="displayModal"
    :header="$t('configuration.schemas.copy')"
    :modal="true"
    :style="{ minWidth: '500px' }"
  >
    <CreateSchemaForm
      :initial-attributes="
        storedSchema.schema.attrNames?.map((attribute) => ({
          name: attribute,
        }))
      "
      :is-copy="true"
      :on-close="handleClose"
      @success="$emit('success')"
    />
  </Dialog>
</template>

<script setup lang="ts">
// Libraries
import { storeToRefs } from 'pinia';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { PropType, ref } from 'vue';
import { useI18n } from 'vue-i18n';
// Source
import { useGovernanceStore, useTenantStore } from '@/store';
import { SchemaStorageRecord } from '@/types';
import { SchemaSendRequest } from '@/types/acapyApi/acapyInterface';
import CreateSchemaForm from './CreateSchemaForm.vue';
import checkSchemaPostedInterval from './checkSchemaPostedInterval';

const props = defineProps({
  storedSchema: {
    type: Object as PropType<SchemaStorageRecord>,
    required: true,
  },
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
const openModal = async (schema: SchemaStorageRecord) => {
  selectedSchema.value = schema;
  displayModal.value = true;
};
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
