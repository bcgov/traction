<template>
  <div>
    <Button
      :disabled="isCreateButtonDisabled"
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
import { computed, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { API_PATH } from '@/helpers/constants';
import { formatSchemaList } from '@/helpers/tableFormatters';
import { useAcapyApi } from '@/store/acapyApi';
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

const { isIssuer, tenantWallet } = storeToRefs(useTenantStore());
const { schemaList, selectedCredentialDefinition } =
  storeToRefs(useGovernanceStore());
const governanceStore = useGovernanceStore();

const formattedSchemaList = computed(() => formatSchemaList(schemaList));

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
    return true; // For non-askar-anoncreds wallets, always allow
  }

  if (!webvhConfig.value) {
    return false;
  }

  const witnesses = webvhConfig.value.witnesses;
  const isConnected = Boolean(
    witnesses && Array.isArray(witnesses) && witnesses.length > 0
  );

  return isConnected;
});

// Disable button logic:
// - For askar wallets: require isIssuer to be true
// - For askar-anoncreds wallets: only require WebVH endorser to be connected
const isCreateButtonDisabled = computed(() => {
  if (isAskarAnoncredsWallet.value) {
    return !isWebvhEndorserConnected.value;
  } else {
    return !isIssuer.value;
  }
});

// Load webvh configuration
const acapyApi = useAcapyApi();
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

// Also reload config when wallet type changes
watch(
  () => isAskarAnoncredsWallet.value,
  (isAnoncreds) => {
    if (isAnoncreds) {
      webvhConfigLoaded.value = false;
      loadWebvhConfig();
    }
  }
);

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
