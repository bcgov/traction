<template>
  <h3 class="mt-0">
    {{ $t('configuration.schemasCreds.credentialDefinitions') }}
  </h3>

  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="formattedstoredCredDefs"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    selection-mode="single"
    data-key="cred_def_id"
    sort-field="created_at"
    :sort-order="-1"
    filter-display="menu"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start"></div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left schema-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.global.value"
              placeholder="Search Cred Defs"
            />
          </span>
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-button-outlined"
            title="Refresh Table"
            @click="loadTable"
          />
        </div>
      </div>
    </template>
    <template #empty>{{ $t('common.noRecordsFound') }}</template>
    <template #loading>{{ $t('common.loading') }}</template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column :sortable="false" header="Actions">
      <template #body="{ data }">
        <Button
          title="Delete Credential Definition"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="deleteCredDef($event, data.cred_def_id)"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="cred_def_id"
      header="ID"
      filter-field="cred_def_id"
      :show-filter-match-modes="false"
    >
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          class="p-column-filter"
          placeholder="Search By ID"
          @input="filterCallback()"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="schema_id"
      header="Schema ID"
      filter-field="schema_id"
      :show-filter-match-modes="false"
    >
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          class="p-column-filter"
          placeholder="Search By Schema ID"
          @input="filterCallback()"
        />
      </template>
    </Column>
    <Column :sortable="true" field="support_revocation" header="Revokable">
      <template #body="{ data }">
        <span v-if="data.support_revocation">
          <i class="pi pi-check-circle"></i>
        </span>
      </template>
    </Column>
    <Column
      :sortable="true"
      field="created"
      header="Created at"
      filter-field="created"
      :show-filter-match-modes="false"
    >
      <template #body="{ data }">
        {{ data.created }}
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
    <template #expansion="{ data }">
      <RowExpandData
        :id="data.cred_def_id"
        :url="API_PATH.CREDENTIAL_DEFINITION_STORAGE"
      />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, Ref, computed } from 'vue';
// PrimeVue etc
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useGovernanceStore } from '../../store';
import { storeToRefs } from 'pinia';
// Custom components
import RowExpandData from '../common/RowExpandData.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const confirm = useConfirm();
const toast = useToast();

const governanceStore = useGovernanceStore();
const { loading, storedCredDefs } = storeToRefs(useGovernanceStore());

const formattedstoredCredDefs: Ref<any[]> = computed(() =>
  storedCredDefs.value.map((credDef: any) => ({
    cred_def_id: credDef.cred_def_id,
    schema_id: credDef.schema_id,
    created_at: credDef.created_at,
    created: formatDateLong(credDef.created_at),
  }))
);
// LOADING the schema list and the stored cred defs
const loadTable = async () => {
  try {
    await governanceStore.listStoredSchemas();
    // Wait til schemas are loaded so the getter can map together the schems to creds
    await governanceStore.listStoredCredentialDefinitions();
  } catch (err) {
    console.error(err);
    toast.error(`Failure: ${err}`);
  }
};

onMounted(async () => {
  loadTable();
});

// Deleting a stored schema
const deleteCredDef = (event: any, id: string) => {
  confirm.require({
    target: event.currentTarget,
    message:
      'Are you sure you want to remove this credential definition from storage?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete(id);
    },
  });
};
const doDelete = (id: string) => {
  governanceStore
    .deleteStoredCredentialDefinition(id)
    .then(() => {
      toast.success(`Credential definition removed from storage`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

// Filter for search
const filter = ref({
  global: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  cred_def_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  schema_id: {
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
.row.buttons {
  float: right;
  margin: 3rem 1rem 0 0;
}

.p-datatable-header input {
  padding-left: 3rem;
  margin-right: 1rem;
}

.create-btn {
  margin-right: 1rem;
}

.schema-search {
  margin-left: 1.5rem;
}
</style>
