<template>

  
  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="credentialExchanges"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['cred_def_id']"
    selection-mode="single"
    data-key="credential_exchange_id"
    sort-field="updated_at"
    :sort-order="-1"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start"></div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left credential-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.cred_def_id.value"
              placeholder="Search Credentials"
            />
          </span>
        </div>
      </div>
    </template>
    <template #empty> No records found. </template>
    <template #loading> Loading data. Please wait... </template>
    <template #expansion="{ data }">
      <CredentialAttributes :attributes="getAttributes(data)" />
      --
      <RowExpandData
        :id="data.credential_exchange_id"
        :url="API_PATH.ISSUE_CREDENTIAL_RECORDS"
      />
    </template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column header="Actions" class="action-col">
      <template #body="{ data }">
        <Button
          title="Accept Credential into Wallet"
          icon="pi pi-check"
          class="p-button-rounded p-button-icon-only p-button-text"
          :class="{ accepted: data.state === 'credential_acked' }"
          :disabled="data.state !== 'offer_received'"
          @click="$emit('accept', $event, data)"
        />
        <Button
          title="Reject Credential Offer"
          icon="pi pi-times"
          class="p-button-rounded p-button-icon-only p-button-text"
          :disabled="data.state !== 'offer_received'"
          @click="$emit('reject', $event, data)"
        />
        <Button
          title="Delete Credential Exchange Record"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          :disabled="data.state === 'offer_received'"
          @click="$emit('delete', $event, data)"
        />
      </template>
    </Column>
    <Column :sortable="true" field="connection_id" header="Connection">
      <template #body="{ data }">
        {{ findConnectionName(data.connection_id) }}
      </template>
    </Column>
    <Column
      :sortable="true"
      field="credential_definition_id"
      header="Credential"
    />
    <Column :sortable="true" field="state" header="Status">
      <template #body="{ data }">
        <StatusChip :status="data.state" />
      </template>
    </Column>
    <Column :sortable="true" field="updated_at" header="Last update">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
  </DataTable>
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
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
// State
import { useContactsStore, useHolderStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import CredentialAttributes from './CredentialAttributes.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

// The emits it can do (common things between table and card view handled in parent)
defineEmits(['accept', 'delete', 'reject']);

// State
const { findConnectionName } = storeToRefs(useContactsStore());
const { loading, credentialExchanges } = storeToRefs(useHolderStore());

// Cred attributes
const getAttributes = (data: V10CredentialExchange): CredAttrSpec[] => {
  return data.credential_offer_dict?.credential_preview?.attributes ?? [];
};

const expandedRows = ref([]);

const filter = ref({
  cred_def_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
});
</script>

<style scoped>
button.accepted {
  color: green !important;
}
</style>
