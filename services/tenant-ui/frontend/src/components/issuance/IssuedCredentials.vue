<template>
  <h3 class="mt-0">{{ $t('issue.credentials') }}</h3>

  <DataTable
    v-model:selection="selectedCredential"
    v-model:filters="filter"
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="formattedCredentials"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    selection-mode="single"
    data-key="credential_exchange_id"
    sort-field="created_at"
    :sort-order="-1"
    filterDisplay="menu"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <OfferCredential />
        </div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left credential-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.global.value"
              placeholder="Search Credentials"
            />
          </span>
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-button-outlined"
            title="Refresh Table"
            @click="loadTable"
          ></Button>
        </div>
      </div>
    </template>
    <template #empty>{{ $t('common.noRecordsFound') }}</template>
    <template #loading>{{ $t('common.loading') }}</template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column header="Actions">
      <template #body="{ data }">
        <DeleteCredentialExchangeButton
          :cred-exch-id="data.credential_exchange_id"
        />

        <RevokeCredentialButton
          :cred-exch-record="data"
          :connection-display="findConnectionName(data.connection_id)"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="credential_definition_id"
      header="Credential Definition"
      filterField="credential_definition_id"
    >
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          @input="filterCallback()"
          class="p-column-filter"
          placeholder="Search By Credential Definition"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="contact"
      header="Contact"
      filter-field="contact"
    >
      <template #body="{ data }">
        {{ data.contact }}
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          @input="filterCallback()"
          class="p-column-filter"
          placeholder="Search By Contact"
        />
      </template>
    </Column>
    <Column :sortable="true" field="state" header="Status" filter-field="state">
      <template #body="{ data }">
        <StatusChip :status="data.state" />
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          @input="filterCallback()"
          class="p-column-filter"
          placeholder="Search By Status"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="created"
      header="Created at"
      filter-field="created"
    >
      <template #body="{ data }">
        {{ data.created }}
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          @input="filterCallback()"
          class="p-column-filter"
          placeholder="Search By Time"
        />
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData
        :id="data.credential_exchange_id"
        :url="API_PATH.ISSUE_CREDENTIAL_RECORDS"
      />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, Ref, computed } from 'vue';
// State
import { useIssuerStore, useContactsStore } from '@/store';
import { storeToRefs } from 'pinia';
// PrimeVue/etc
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'vue-toastification';
// Other Components
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';
import DeleteCredentialExchangeButton from './deleteCredential/DeleteCredentialExchangeButton.vue';
import OfferCredential from './offerCredential/OfferCredential.vue';
import RevokeCredentialButton from './deleteCredential/RevokeCredentialButton.vue';
import RowExpandData from '../common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';

const toast = useToast();

const contactsStore = useContactsStore();
const { contacts } = storeToRefs(useContactsStore());
const issuerStore = useIssuerStore();
// use the loading state from the store to disable the button...
const { loading, credentials, selectedCredential } = storeToRefs(
  useIssuerStore()
);
const findConnectionName = (connectionId: string): string => {
  const connection = contacts.value?.find((c: any) => {
    return c.connection_id === connectionId;
  });
  return (connection ? connection.alias : '...') as string;
};

const formattedCredentials: Ref<any[]> = computed(() =>
  credentials.value.map((cred: any) => ({
    connection_id: cred.connection_id,
    contact: findConnectionName(cred.connection_id),
    credential_definition_id: cred.credential_definition_id,
    sent_time: cred.sent_time,
    created: formatDateLong(cred.created_at),
    created_at: cred.created_at,
  }))
);

// Get the credentials
const loadTable = async () => {
  await issuerStore.listCredentials().catch((err) => {
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
  await loadTable();
});

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

// Filter for search
const filter = ref({
  global: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  contact: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  credential_definition_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
});
</script>

<style scoped>
.credential-search {
  margin-left: 1.5rem;
}
.credential-search input {
  padding-left: 3rem !important;
  margin-right: 1rem;
}
</style>
