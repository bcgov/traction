<template>
  <h3 class="mt-0">{{ t('configuration.schemasCreds.schemas') }}</h3>

  <DataTable
    v-model:selection="selectedSchemaTemplate"
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="schemaTemplates"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['schema_id', 'version']"
    selection-mode="single"
    data-key="schema_id"
    sort-field="created_at"
    :sort-order="-1"
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
    <Column
      :sortable="true"
      field="schema.name"
      header="Name"
      filter-field="name"
    />
    <Column
      :sortable="true"
      field="schema_id"
      header="Schema ID"
      filter-field="schema_id"
    />
    <Column :sortable="true" field="schema.version" header="Version" />
    <Column :sortable="true" field="schema.attrNames" header="Attributes" />

    <Column :sortable="true" field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <!-- <Column
      :sortable="true"
      field="credential_templates"
      header="Credential Template"
    >
      <template #body="{ data }">
        <CreateCredentialTemplate :schema-template="data" />
      </template>
    </Column> -->
    <template #expansion="{ data }">
      <RowExpandData :id="data.schema_id" :url="API_PATH.SCHEMA_STORAGE" />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue etc
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
// State
import { useGovernanceStore } from '../../store';
import { storeToRefs } from 'pinia';
// Custom components
import CreateSchema from './createSchema/CreateSchema.vue';
import CopySchema from './copySchema/CopySchema.vue';
import CreateCredentialTemplate from './credentialtemplate/CreateCredentialTemplate.vue';
import RowExpandData from '../common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const confirm = useConfirm();
const toast = useToast();
const { t } = useI18n();

const governanceStore = useGovernanceStore();
const { loading, schemaTemplates, selectedSchemaTemplate } = storeToRefs(
  useGovernanceStore()
);

// Loading the schema list
const loadTable = async () => {
  governanceStore.listStoredSchemas().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
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
  schema_id: { value: null, matchMode: FilterMatchMode.CONTAINS },
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
