<template>
  <div>
    <Button
      :disabled="isCreateButtonDisabled"
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
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
// Source
import { API_PATH } from '@/helpers/constants';
import { useAcapyApi } from '@/store/acapyApi';
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
const acapyApi = useAcapyApi();

const { isIssuer, tenantWallet } = storeToRefs(useTenantStore());
const { selectedSchema } = storeToRefs(useGovernanceStore());
const governanceStore = useGovernanceStore();

// WebVH configuration state
const webvhConfig = ref<any>(null);
const webvhConfigLoaded = ref(false);

// Check if wallet is askar-anoncreds
const isAskarAnoncredsWallet = computed(() => {
  return tenantWallet?.value?.settings?.['wallet.type'] === 'askar-anoncreds';
});

// Check if webvh endorser is connected
const isWebvhEndorserConnected = computed(() => {
  if (!isAskarAnoncredsWallet.value) {
    // For non-askar-anoncreds wallets, always allow schema creation
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
    !isIssuer?.value ||
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
