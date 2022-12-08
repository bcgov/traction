<template>
  <h3 class="mt-0">Schemas</h3>

  <DataTable
    v-model:selection="selectedSchemaTemplate"
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="schemaTemplates"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['name', 'version']"
    selection-mode="single"
    data-key="schema_template_id"
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
              v-model="filter.name.value"
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
    <template #empty> No records found. </template>
    <template #loading> Loading data. Please wait... </template>
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
    <Column :sortable="true" field="name" header="Schema" filter-field="name" />
    <Column :sortable="true" field="version" header="Version" />
    <Column :sortable="true" field="status" header="Status">
      <template #body="{ data }">
        <StatusChip :status="data.status" />
      </template>
    </Column>
    <Column :sortable="true" field="attributes" header="Attributes" />
    <Column
      :sortable="true"
      field="credential_templates"
      header="Credential Template"
    >
      <template #body="{ data }">
        <CreateCredentialTemplate :schema-template="data" />
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData
        :id="data.schema_template_id"
        :url="API_PATH.GOVERNANCE_SCHEMA_TEMPLATES"
        :params="{ acapy: true, credential_templates: true }"
      />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';

// Custom components
import CreateSchema from './createSchema/CreateSchema.vue';
import CopySchema from './copySchema/CopySchema.vue';
import CreateCredentialTemplate from './credentialtemplate/CreateCredentialTemplate.vue';
import RowExpandData from '../common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';

import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
import { useGovernanceStore } from '../../store';
import { storeToRefs } from 'pinia';

const confirm = useConfirm();
const toast = useToast();

const governanceStore = useGovernanceStore();
// use the loading state from the store to disable the button...
const { loading, schemaTemplates, selectedSchemaTemplate } = storeToRefs(
  useGovernanceStore()
);

const loadTable = async () => {
  governanceStore.listSchemaTemplates().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});

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
    .deleteSchema(schema)
    .then(() => {
      toast.success(`Schema successfully deleted`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};

// -----------------------------------------------/Loading schemas

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

const filter = ref({
  version: { value: null, matchMode: FilterMatchMode.CONTAINS },
  name: { value: null, matchMode: FilterMatchMode.CONTAINS },
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
