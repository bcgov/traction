<template>
  <div>
    <Button
      :disabled="!isIssuer"
      :label="$t('configuration.credentialDefinitions.create')"
      icon="pi pi-plus"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="$t('configuration.credentialDefinitions.create')"
      :modal="true"
      :style="{ minWidth: '500px' }"
    >
      <CreateCredentialDefinitionForm
        :schemas="formattedSchemaList"
        @success="$emit('success')"
        @closed="handleClose"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { formatSchemaList } from '@/helpers/tableFormatters';
import { useGovernanceStore, useTenantStore } from '@/store';
import { CredentialDefinitionSendRequest } from '@/types/acapyApi/acapyInterface';
import CreateCredentialDefinitionForm from './CreateCredentialDefinitionForm.vue';
import checkCredDefPostedInterval from './checkCredDefPostedInterval';

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
const { schemaList, selectedCredentialDefinition } =
  storeToRefs(useGovernanceStore());
const governanceStore = useGovernanceStore();

const formattedSchemaList = computed(() => formatSchemaList(schemaList));

// Modal
const displayModal = ref(false);
const openModal = async () => (displayModal.value = true);
const handleClose = (credDef: CredentialDefinitionSendRequest) => {
  displayModal.value = false;
  checkCredDefPostedInterval(
    credDef,
    governanceStore.getStoredCredDefs,
    props.tableReload,
    t('configuration.credentialDefinitions.postFinished'),
    selectedCredentialDefinition
  );
};
</script>
