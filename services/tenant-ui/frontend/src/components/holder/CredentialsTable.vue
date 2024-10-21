<template>
  <DataTable
    v-model:expanded-rows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="formattedCredentialExchanges"
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
          <IconField icon-position="left">
            <InputIcon><i class="pi pi-search" /></InputIcon>
            <InputText
              v-model="filter.cred_def_id.value"
              placeholder="Search Credentials"
            />
          </IconField>
        </div>
      </div>
    </template>
    <template #empty>{{ $t('common.noRecordsFound') }}</template>
    <template #loading>{{ $t('common.loading') }}</template>
    <template #expansion="{ data }: { data: FormattedHeldCredentialRecord }">
      <CredentialAttributes :attributes="data.credential_attributes" />
      <hr class="expand-divider" />
      <RowExpandData
        :id="data.credential_exchange_id"
        :url="API_PATH.ISSUE_CREDENTIAL_20_RECORDS"
      />
    </template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column header="Actions" class="action-col">
      <template #body="{ data }: { data: FormattedHeldCredentialRecord }">
        <Button
          title="Accept Credential into Wallet"
          icon="pi pi-check"
          class="p-button-rounded p-button-icon-only p-button-text"
          :class="{ accepted: data.state === 'done' }"
          :disabled="data.state !== 'offer-received'"
          @click="$emit('accept', $event, data)"
        />
        <Button
          title="Reject Credential Offer"
          icon="pi pi-times"
          class="p-button-rounded p-button-icon-only p-button-text"
          :disabled="data.state !== 'offer-received'"
          @click="$emit('reject', $event, data)"
        />
        <Button
          title="Delete Credential Exchange Record"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          :disabled="data.state === 'offer-received'"
          @click="$emit('delete', $event, data)"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="connection"
      header="Connection"
      filter-field="connection"
      :show-filter-match-modes="false"
    >
      <template #body="{ data }">
        <LoadingLabel :value="data.connection" />
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
      :show-filter-match-modes="false"
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
      :show-filter-match-modes="false"
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
      :show-filter-match-modes="false"
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
import { FormattedHeldCredentialRecord } from '@/helpers/tableFormatters';

// Vue
import { computed, onMounted, ref } from 'vue';
// PrimeVue
import { FilterMatchMode } from 'primevue/api';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import InputIcon from 'primevue/inputicon';
import IconField from 'primevue/iconfield';
import { useToast } from 'vue-toastification';
// State
import { useConnectionStore, useHolderStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import RowExpandData from '@/components/common/RowExpandData.vue';
import { formatHeldCredentials } from '@/helpers/tableFormatters';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import LoadingLabel from '../common/LoadingLabel.vue';
import StatusChip from '../common/StatusChip.vue';
import CredentialAttributes from './CredentialAttributes.vue';

// The emits it can do (common things between table and card view handled in parent)
defineEmits(['accept', 'delete', 'reject']);

const toast = useToast();

// State
const { listConnections, findConnectionName } = useConnectionStore();
const { connections } = storeToRefs(useConnectionStore());
const { loading, credentialExchanges } = storeToRefs(useHolderStore());
const holderStore = useHolderStore();

// The data table row format
const formattedCredentialExchanges = computed(() =>
  formatHeldCredentials(credentialExchanges, findConnectionName)
);

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
  connection: {
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

  // Load connections if not already there for display
  if (!connections.value || !connections.value.length) {
    listConnections().catch((err) => {
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
</style>
