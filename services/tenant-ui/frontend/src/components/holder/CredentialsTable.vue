<template>
  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="formattedcredentialExchanges"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['cred_def_id']"
    selection-mode="single"
    data-key="credential_exchange_id"
    sort-field="updated_at"
    :sort-order="-1"
    filter-display="menu"
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
    <template #empty>{{ $t('common.noRecordsFound') }}</template>
    <template #loading>{{ $t('common.loading') }}</template>
    <template #expansion="{ data }">
      <CredentialAttributes :attributes="getAttributes(data)" />
      <hr class="expand-divider" />
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
    <Column
      :sortable="true"
      field="connection_id"
      header="Connection"
      filter-field="credential_id"
      :showFilterMatchModes="false"
    >
      <template #body="{ data }">
        {{ findConnectionName(data.connection_id) }}
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          class="p-column-filter"
          placeholder="Search By Connection"
          @input="filterCallback()"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="credential_definition_id"
      header="Credential"
      filter-field="credential_definition_id"
      :showFilterMatchModes="false"
    >
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          class="p-column-filter"
          placeholder="Search By Credential"
          @input="filterCallback()"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="state"
      header="Status"
      filter-field="state"
      :showFilterMatchModes="false"
    >
      <template #body="{ data }">
        <StatusChip :status="data.state" />
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          class="p-column-filter"
          placeholder="Search By Status"
          @input="filterCallback()"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="updated"
      header="Last update"
      filter-field="updated"
      :showFilterMatchModes="false"
    >
      <template #body="{ data }">
        {{ data.updated }}
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          class="p-column-filter"
          placeholder="Search By Time"
          @input="filterCallback()"
        />
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
import { onMounted, ref, computed } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
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

const toast = useToast();

// State
const contactsStore = useContactsStore();
const { contacts, findConnectionName } = storeToRefs(useContactsStore());
const { loading, credentialExchanges } = storeToRefs(useHolderStore());
const holderStore = useHolderStore();
const formattedcredentialExchanges = computed(() =>
  credentialExchanges.value.map((ce) => ({
    connection_id: ce.connection_id,
    credential_definition_id: ce.credential_definition_id,
    state: ce.state,
    updated: formatDateLong(ce.updated_at ?? ''),
    updated_at: ce.updated_at,
    created: formatDateLong(ce.created_at ?? ''),
    created_at: ce.created_at,
  }))
);

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
  credential_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  credential_definition_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  state: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  updated: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
});

// Get the credential exchange list when loading the component
const loadCredentials = async () => {
  holderStore.listHolderCredentialExchanges().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });

  // Load contacts if not already there for display
  if (!contacts.value || !contacts.value.length) {
    contactsStore.listContacts().catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
};

onMounted(async () => {
  loadCredentials();
});
</script>

<style scoped>
button.accepted {
  color: green !important;
}

.expand-divider {
  border: 1px dashed grey;
  width: 40px;
  margin-inline-start: 0;
}
</style>
