<template>
  <h3 class="mt-0">Schemas</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable
      v-model:selection="selectedSchemaTemplate"
      :value="schemaTemplates"
      :paginator="true"
      :rows="10"
      striped-rows
      selection-mode="single"
    >
      <template #header>
        <div class="flex justify-content-between">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText
              v-model="schemaTemplateFilters"
              placeholder="Schema Search"
              disabled
            />
          </span>
        </div>
        <Button
          icon="pi pi-refresh"
          class="p-button-rounded p-button-outlined btn-refresh-table"
          title="Refresh Table"
          @click="loadTable"
        ></Button>
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
            :schema-template-id="data.schema_template_id"
            v-if="!data.credential_templates.length"
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
import { ref, onMounted } from "vue";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import ProgressSpinner from "primevue/progressspinner";
import Dialog from "primevue/dialog";

// Custom components
import CreateSchema from "./CreateSchema.vue";
import CopySchema from "./CopySchema.vue";
import CreateCredentialTemplate from "./credentialtemplate/CreateCredentialTemplate.vue";

import { useConfirm } from "primevue/useconfirm";
import { useToast } from "vue-toastification";
import { useGovernanceStore } from "../../store";
import { storeToRefs } from "pinia";

const confirm = useConfirm();
const toast = useToast();

const governanceStore = useGovernanceStore();
// use the loading state from the store to disable the button...
const {
  loading,
  schemaTemplates,
  selectedSchemaTemplate,
  schemaTemplateFilters,
} = storeToRefs(useGovernanceStore());

const loadTable = async () => {
  governanceStore.listSchemaTemplates().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});

const displayCreateSchema = ref(false);
const createSchema = () => {
  displayCreateSchema.value = !displayCreateSchema.value;
};
const schemaCreated = async () => {
  // this is not getting called... bug? or need to find a new pattern (works on Contacts).
  console.log(
    'schema created emit - do we want to "manually" load contacts or have the store automatically do it?'
  );
  loadTable();
};

const deleteSchema = (event: any, schema: any) => {
  confirm.require({
    target: event.currentTarget,
    message: "Are you sure you want to delete this schema?",
    header: "Confirmation",
    icon: "pi pi-exclamation-triangle",
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

const displayCopySchema = ref(false);
const copySchema = () => {
  displayCopySchema.value = !displayCopySchema.value;
};
const schemaCopied = async () => {
  // this is not getting called... bug? or need to find a new pattern (works on Contacts).
  console.log(
    'schema copied emit - do we want to "manually" load contacts or have the store automatically do it?'
  );
  loadTable();
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
.btn-refresh-table {
  position: absolute;
  right: 12px;
  top: 12px;
}
</style>
