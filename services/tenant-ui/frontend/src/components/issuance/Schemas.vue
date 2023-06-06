<template>
  <h3 class="mt-0">{{ $t('configuration.schemasCreds.schemas') }}</h3>

  <DataTable
    v-model:selection="selectedSchema"
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="formattedSchemaList"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['schema_id', 'version']"
    selection-mode="single"
    data-key="schema_id"
    sort-field="created_at"
    :sort-order="-1"
    filter-display="menu"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <CreateSchema />
          <CopySchema class="ml-4" />
        </div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left schema-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.schema_id.value"
              placeholder="Search Schemas"
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
          title="Delete Schema"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="deleteSchema($event, data)"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="schema.name"
      header="Name"
      filter-field="schema.name"
      :showFilterMatchModes="false"
    >
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          class="p-column-filter"
          placeholder="Search By Name"
          @input="filterCallback()"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="schema_id"
      header="Schema ID"
      filter-field="schema_id"
      :showFilterMatchModes="false"
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
    <Column
      :sortable="true"
      field="schema.version"
      header="Version"
      filter-field="schema.version"
      :showFilterMatchModes="false"
    >
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          class="p-column-filter"
          placeholder="Search By Version"
          @input="filterCallback()"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="schema.attrNames"
      header="Attributes"
      filter-field="schema.attrNames"
      :showFilterMatchModes="false"
    >
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          class="p-column-filter"
          placeholder="Search By Attributes"
          @input="filterCallback()"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="created"
      header="Created at"
      filter-field="created"
      :showFilterMatchModes="false"
    >
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
    <Column
      :sortable="true"
      field="credential_templates"
      header="Credential Definition"
    >
      <template #body="{ data }">
        <CreateCredentialDefinition :schema="data" @success="loadTable" />
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData :id="data.schema_id" :url="API_PATH.SCHEMA_STORAGE" />
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
import CreateSchema from './createSchema/CreateSchema.vue';
import CopySchema from './copySchema/CopySchema.vue';
import CreateCredentialDefinition from './createCredentialDefinition/CreateCredentialDefinition.vue';
import RowExpandData from '../common/RowExpandData.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const confirm = useConfirm();
const toast = useToast();

const governanceStore = useGovernanceStore();
const { loading, schemaList, selectedSchema } = storeToRefs(
  useGovernanceStore()
);

const formattedSchemaList = computed(() =>
  schemaList.value.map((schema) => ({
    schema: {
      name: schema.schema.name,
      version: schema.schema.version,
      attrNames: schema.schema.attrNames,
    },
    schema_id: schema.schema_id,
    created: formatDateLong(schema.created_at),
    created_at: schema.created_at,
    credentialDefinition: schema.credentialDefinition,
  }))
);
// Loading the schema list and the stored cred defs
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
const deleteSchema = (event: any, schema: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this schema?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete(schema);
    },
  });
};
const doDelete = (schema: any) => {
  governanceStore
    .deleteSchema(schema.schema_id)
    .then(() => {
      toast.success(`Schema successfully deleted`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

const filter = ref({
  schema_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  'schema.name': {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  'schema.version': {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  'schema.attrNames': {
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
