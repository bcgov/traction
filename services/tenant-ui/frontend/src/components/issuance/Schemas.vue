<template>
  <h3 class="mt-0">Schemas</h3>

  <DataTable
    v-model:selection="selectedSchemaTemplate"
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="schemaTemplates"
    :paginator="true"
    :rows="10"
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
          icon="pi pi-times-circle"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="deleteSchema($event, data)"
        />
      </template>
    </Column>
    <Column field="name" header="Schema" filter-field="name" />
    <Column field="version" header="Version" />
    <Column field="status" header="Status" />
    <Column field="attributes" header="Attributes" />
    <Column field="credential_templates" header="Credential Template">
      <template #body="{ data }">
        <CreateCredentialTemplate
          v-if="!data.credential_templates.length"
          :schema-template-id="data.schema_template_id"
        />
        <div v-else>
          {{
            `${data.credential_templates[0].name}:${data.credential_templates[0].tag}`
          }}
        </div>
      </template>
    </Column>
    <template #expansion="{ data }">
      <SchemaRowExpandData :row="data" />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';

// Custom components
import CreateSchema from './createSchema/CreateSchema.vue';
import CopySchema from './copySchema/CopySchema.vue';
import CreateCredentialTemplate from './credentialtemplate/CreateCredentialTemplate.vue';
import SchemaRowExpandData from './SchemaRowExpandData.vue';

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
</script>

<style scoped>
.row.buttons {
  float: right;
  margin: 3rem 1rem 0 0;
}

.p-datatable-header input {
  padding-left: 3rem;
}

.create-btn {
  margin-right: 1rem;
}
</style>
