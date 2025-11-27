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
      :disabled="isCreateButtonDisabled"
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
import { computed, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import { API_PATH } from '@/helpers/constants';
import { useAcapyApi } from '@/store/acapyApi';
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
const acapyApi = useAcapyApi();

const { isIssuer, tenantWallet } = storeToRefs(useTenantStore());
const { selectedCredentialDefinition } = storeToRefs(useGovernanceStore());
const governanceStore = useGovernanceStore();

// Check if wallet is askar-anoncreds
const isAskarAnoncredsWallet = computed(() => {
  return tenantWallet.value?.settings?.['wallet.type'] === 'askar-anoncreds';
});

// WebVH configuration state
const webvhConfig = ref<any>(null);
const webvhConfigLoaded = ref(false);

// Check if webvh endorser is connected
const isWebvhEndorserConnected = computed(() => {
  if (!isAskarAnoncredsWallet.value) {
    // For non-askar-anoncreds wallets, always allow credential definition creation
    return true;
  }

  // For askar-anoncreds wallets, check webvh configuration
  // Check if witnesses array exists and has entries (indicates connection)
  if (
    webvhConfig.value?.witnesses &&
    Array.isArray(webvhConfig.value.witnesses)
  ) {
    return webvhConfig.value.witnesses.length > 0;
  }

  return false;
});

// Disable button if askar-anoncreds wallet and webvh endorser is not connected
const isCreateButtonDisabled = computed(() => {
  return (
    !isIssuer.value ||
    (isAskarAnoncredsWallet.value && !isWebvhEndorserConnected.value)
  );
});

// Load webvh configuration
const loadWebvhConfig = async () => {
  if (!isAskarAnoncredsWallet.value) {
    webvhConfigLoaded.value = true;
    return;
  }

  try {
    const response = await acapyApi.getHttp(API_PATH.DID_WEBVH_CONFIG);
    const configData = response?.data ?? response ?? null;
    const isEmptyConfig =
      !configData ||
      (typeof configData === 'object' && Object.keys(configData).length === 0);
    webvhConfig.value = isEmptyConfig ? null : configData;
  } catch (_error) {
    webvhConfig.value = null;
  } finally {
    webvhConfigLoaded.value = true;
  }
};

onMounted(() => {
  loadWebvhConfig();
});

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
