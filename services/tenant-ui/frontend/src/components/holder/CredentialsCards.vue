<template>
  <div v-if="loading || loadingOca" class="grid">
    <div class="col-12 md:col-6 xl:col-3">
      <SkeletonCard />
    </div>
  </div>

  <div v-else class="grid">
    <div
      v-for="cred in credentialExchanges"
      v-if="credentialExchanges && credentialExchanges.length"
      class="col-12 md:col-6 xl:col-3"
    >
      <OcaCard :credential="cred" />
    </div>

    <span v-else> There are no credentials in your Wallet </span>
  </div>
</template>

<script setup lang="ts">
// Types
import {
  CredAttrSpec,
  V10CredentialExchange,
} from '@/types/acapyApi/acapyInterface';

// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Card from 'primevue/card';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
// State
import { useContactsStore, useHolderStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import CredentialAttributes from './CredentialAttributes.vue';
import OcaCard from './credentialOcaCard/OcaCard.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';
import SkeletonCard from '@/components/common/SkeletonCard.vue';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

// The emits it can do (common things between table and card view handled in parent)
defineEmits(['accept', 'delete', 'reject']);

// State
const { findConnectionName } = storeToRefs(useContactsStore());
const { loading, loadingOca, credentialExchanges } = storeToRefs(
  useHolderStore()
);

// Cred attributes
const getAttributes = (data: V10CredentialExchange): CredAttrSpec[] => {
  return data.credential_offer_dict?.credential_preview?.attributes ?? [];
};
</script>

<style scoped>
button.accepted {
  color: green !important;
}
</style>
