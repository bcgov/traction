<template>
  <div>
    <Button
      v-tooltip="
        disableReason === 'not_issuer'
          ? $t('configuration.schemas.notIssuer')
          : disableReason === 'webvh_not_connected'
            ? $t('identifiers.webvh.configureDescription')
            : ''
      "
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
  const walletType = tenantWallet?.value?.settings?.['wallet.type'];
  console.log('Wallet type check:', {
    walletType,
    isAskarAnoncreds: walletType === 'askar-anoncreds',
    tenantWallet: tenantWallet?.value,
  });
  return walletType === 'askar-anoncreds';
});

// Check if webvh endorser is connected
const isWebvhEndorserConnected = computed(() => {
  if (!isAskarAnoncredsWallet.value) {
    // For non-askar-anoncreds wallets, always allow schema creation
    return true;
  }

  // For askar-anoncreds wallets, check webvh configuration
  // Check if witnesses array exists and has entries (indicates connection)
  const hasWitnesses = Boolean(
    webvhConfig.value?.witnesses &&
      Array.isArray(webvhConfig.value.witnesses) &&
      webvhConfig.value.witnesses.length > 0
  );

  console.log('isWebvhEndorserConnected check:', {
    isAskarAnoncreds: isAskarAnoncredsWallet.value,
    hasWitnesses,
    witnesses: webvhConfig.value?.witnesses,
  });

  return hasWitnesses;
});

// Disable button logic:
// - For askar wallets: require isIssuer to be true
// - For askar-anoncreds wallets: only require WebVH endorser to be connected
const isCreateButtonDisabled = computed(() => {
  if (isAskarAnoncredsWallet.value) {
    // For askar-anoncreds wallets, only check WebVH connection
    const webvhNotConnected = !isWebvhEndorserConnected.value;
    console.log('isCreateButtonDisabled check (askar-anoncreds):', {
      isAskarAnoncreds: true,
      isWebvhConnected: isWebvhEndorserConnected.value,
      webvhNotConnected,
      disabled: webvhNotConnected,
    });
    return webvhNotConnected;
  } else {
    // For askar wallets, require issuer status
    const notIssuer = !isIssuer?.value;
    console.log('isCreateButtonDisabled check (askar):', {
      isAskarAnoncreds: false,
      notIssuer,
      disabled: notIssuer,
    });
    return notIssuer;
  }
});

// Debug info for why button is disabled
const disableReason = computed(() => {
  if (isAskarAnoncredsWallet.value) {
    // For askar-anoncreds, only check WebVH connection
    if (!isWebvhEndorserConnected.value) {
      return 'webvh_not_connected';
    }
  } else {
    // For askar wallets, check issuer status
    if (!isIssuer?.value) {
      return 'not_issuer';
    }
  }
  return null;
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
    console.log('WebVH Config:', webvhConfig.value);
    console.log('Witnesses array:', webvhConfig.value?.witnesses);
    console.log('Is connected:', isWebvhEndorserConnected.value);
  } catch (_error) {
    console.error('Error loading WebVH config:', _error);
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
