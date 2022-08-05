<template>
  <h3 class="mt-0">Schemas</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable
      :value="store.state.schemas.data"
      :paginator="true"
      :rows="10"
      striped-rows
      v-model:selection="store.state.schemas.selection"
      selection-mode="single"
    >
      <template #header>
        <div class="flex justify-content-between">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText
              v-model="store.state.schemas.filters"
              placeholder="Schema Search"
            />
          </span>
        </div>
      </template>
      <Column field="name" header="Schema" filterField="name" />
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
      @click="toggleAddSchema"
    />
  </div>
</template>

<script setup lang="ts">
// Vue
import { inject, ref, onMounted } from "vue";

// PrimeVue
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import ProgressSpinner from "primevue/progressspinner";

// Other imports
import axios from "axios";

// Custom components
import CreateSchema from "./CreateSchema.vue";

// Store
const store: any = inject("store");

// ----------------------------------------------------------------
// Loading schemas
// ----------------------------------------------------------------
let loading = ref(true);

onMounted(() => {
  loading.value = true;

  axios
    .get("/api/traction/tenant/v1/governance/schema_templates", {
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${store.state.token}`,
      },
    })
    .then((res) => {
      store.state.schemas.data = res.data.items;
      console.log(store.state.schemas.data);
      loading.value = false;
    })
    .catch((err) => {
      store.state.schemas.data = null;
      console.error("error", err);
    });
});

const toggleAddSchema = () => {
  store.state.schemas.addSchema = !store.state.schemas.addSchema;
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
