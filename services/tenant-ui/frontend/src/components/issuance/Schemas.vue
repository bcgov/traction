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
            />
          </span>
        </div>
      </template>
      <Column field="name" header="Schema" filter-field="name" />
      <Column field="version" header="Version" />
      <Column field="status" header="Status" />
      <Column field="state" header="State" />
      <Column field="attributes" header="Attributes" />
      <Column field="schema_id" header="ID" />
    </DataTable>
    <Button
      class="create-btn"
      icon="pi pi-plus"
      label="Create Schema"
      @click="createSchema"
    />
    <Dialog v-model:visible="displayAddSchema" header="Create a new schema">
      <CreateSchema @created="schemaCreated"></CreateSchema>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { inject, ref, onMounted } from "vue";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import ProgressSpinner from "primevue/progressspinner";
import Dialog from "primevue/dialog";

// Custom components
import CreateSchema from "./CreateSchema.vue";

import { useToast } from "vue-toastification";
import { useGovernanceStore } from "../../store";
import { storeToRefs } from "pinia";

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

const displayAddSchema = ref(false);

const createSchema = () => {
  displayAddSchema.value = !displayAddSchema.value;
};

const schemaCreated = async () => {
  // Emited from the schema creation component when a successful invite is made
  console.log('schema created emit - do we want to "manually" load schemas or have the store automatically do it?');
  loadTable();
};
// -----------------------------------------------/Loading schemas
</script>

<style scoped>
.create-btn {
  float: right;
  margin: 3rem 1rem 0 0;
}
.p-datatable-header input {
  padding-left: 3rem;
}
</style>
