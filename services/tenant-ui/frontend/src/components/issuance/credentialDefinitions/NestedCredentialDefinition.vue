<template>
  <div class="container">
    <div
      v-for="cred in props.schema.credentialDefinitions"
      :key="cred.cred_def_id"
      v-tooltip="{
        value: `${cred.cred_def_id}`,
        escape: true,
      }"
      class="pi pi-id-card text-3xl ml-2"
      @click="navigateToCredDef(cred)"
    ></div>
    <Button
      v-tooltip.top="$t('configuration.credentialDefinitions.create')"
      :disabled="!isIssuer"
      icon="pi pi-plus"
      class="p-button-text"
      @click="openModal"
    />
  </div>
  <Dialog
    v-model:visible="displayModal"
    :header="$t('configuration.credentialDefinitions.create')"
    :style="{ minWidth: '400px' }"
    :modal="true"
  >
    <CreateCredentialDefinitionForm
      :schema="schema"
      @success="$emit('success')"
      @closed="handleClose"
    />
  </Dialog>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import { useGovernanceStore, useTenantStore } from '@/store';
import { CredentialDefinitionSendRequest } from '@/types/acapyApi/acapyInterface';
import CreateCredentialDefinitionForm from './CreateCredentialDefinitionForm.vue';
import checkCredDefPostedInterval from './checkCredDefPostedInterval';

const props = defineProps({
  schema: {
    type: Object,
    required: true,
  },
  tableReload: {
    type: Function,
    required: false,
    default: () => {},
  },
});

defineEmits(['success']);

const router = useRouter();
const { t } = useI18n();
const { isIssuer } = storeToRefs(useTenantStore());
const { selectedCredentialDefinition } = storeToRefs(useGovernanceStore());
const governanceStore = useGovernanceStore();

const navigateToCredDef = (cred: any) => {
  selectedCredentialDefinition.value = cred;
  router.push({ name: 'CredentialDefinitions' });
};

// Modal
const displayModal = ref(false);
const openModal = async () => (displayModal.value = true);
const handleClose = async (credDef: CredentialDefinitionSendRequest) => {
  displayModal.value = false;
  await checkCredDefPostedInterval(
    credDef,
    governanceStore.getStoredCredDefs,
    props.tableReload,
    t('configuration.credentialDefinitions.postFinished')
  );
};
</script>

<style scoped>
.container {
  max-width: 300px;
  display: flex;
}
.pi.pi-id-card {
  display: flex;
  align-items: center;
}
.pi-id-card:hover {
  color: black;
  text-shadow: 0 0 2px black;
}
</style>
