<template>
  <h3 class="mt-0">Schemas</h3>

  <DataTable
    v-model:selection="selectedSchemaTemplate"
    :loading="loading"
    :value="schemaTemplates"
    :paginator="true"
    :rows="10"
    striped-rows
    selection-mode="single"
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
    <template #empty> No schemas found. </template>
    <template #loading> Loading schema data. Please wait... </template>
    <Column :sortable="false" header="Actions">
      <template #body="{ data }">
        <Button
          title="Delete Schema"
          icon="pi pi-times"
          class="p-button-rounded p-button-icon-only p-button-danger p-button-text"
          @click="deleteSchema($event, data)"
        />
      </template>
      <Column :sortable="false" header="Actions">
        <template #body="{ data }">
          <Button
            title="Delete Schema"
            icon="pi pi-times"
            class="p-button-rounded p-button-icon-only p-button-danger p-button-text"
            @click="deleteSchema($event, data)"
          />
        </template>
      </Column>
      <Column field="name" header="Schema" filter-field="name" />
      <Column field="version" header="Version" />
      <Column field="status" header="Status" />
      <Column field="state" header="State" />
      <Column field="attributes" header="Attributes" />
      <Column field="schema_id" header="ID" />
      <Column field="credential_templates" header="Credential Template">
        <template #body="{ data }">
          <CreateCredentialTemplate
            v-if="!data.credential_templates.length"
            :disabled="!isIssuer"
            :schema-template-id="data.schema_template_id"
          />
          <div v-else>
            {{
              `${data.credential_templates[0].name}:${data.credential_templates[0].tag}`
            }}
          </div>
        </template>
      </Column>
    </DataTable>
    <div class="row buttons">
      <Button
        v-if="schemaTemplates"
        :disabled="!isIssuer"
        class="create-btn"
        icon="pi pi-plus"
        label="Create Schema"
        @click="createSchema"
      ></Button>
      <Button
        v-if="schemaTemplates"
        class="copy-btn"
        icon="pi pi-copy"
        label="Copy Schema"
        @click="copySchema"
      />
    </div>
    <Dialog
      v-model:visible="displayCreateSchema"
      header="Create a new schema"
      :modal="true"
    >
      <CreateSchema @success="schemaCreated" />
    </Dialog>
    <Dialog
      v-model:visible="displayCopySchema"
      header="Copy an existing schema"
      :modal="true"
    >
      <CopySchema @success="schemaCopied" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';

// Custom components
import CreateSchema from './createSchema/CreateSchema.vue';
import CopySchema from './copySchema/CopySchema.vue';
import CreateCredentialTemplate from './credentialtemplate/CreateCredentialTemplate.vue';

import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
import { useGovernanceStore, useTenantStore } from '../../store';
import { storeToRefs } from 'pinia';

const confirm = useConfirm();
const toast = useToast();

const governanceStore = useGovernanceStore();
const tenantStore = useTenantStore();
// use the loading state from the store to disable the button...
const {
  loading,
  schemaTemplates,
  selectedSchemaTemplate,
  schemaTemplateFilters,
} = storeToRefs(useGovernanceStore());

const { isIssuer } = storeToRefs(useTenantStore());

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
