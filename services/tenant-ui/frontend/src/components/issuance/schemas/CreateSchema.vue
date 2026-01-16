<template>
  <div>
    <Button
      v-tooltip="
        disableReason === 'not_issuer'
          ? $t('configuration.schemas.notIssuer')
          : ''
      "
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
import { computed, onMounted, ref, watch } from 'vue';
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

const tenantStore = useTenantStore();
const { isIssuer, isAskarAnoncredsWallet } = storeToRefs(tenantStore);
const { selectedSchema } = storeToRefs(useGovernanceStore());
const governanceStore = useGovernanceStore();

// Debug info for why button is disabled
const disableReason = computed(() => {
  if (!isIssuer?.value) {
    return 'not_issuer';
  }
  return null;
});

// Load wallet DIDs when component mounts
onMounted(() => {
  if (isAskarAnoncredsWallet?.value) {
    tenantStore.getWalletDids();
  }
});

// Also reload DIDs when wallet type changes (in case wallet loads after mount)
watch(
  () => isAskarAnoncredsWallet?.value,
  (isAnoncreds) => {
    if (isAnoncreds) {
      tenantStore.getWalletDids();
    }
  }
);

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
