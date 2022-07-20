<script setup lang="ts">
import { inject } from "vue";
import Fieldset from "primevue/fieldset";
import Button from "primevue/button";
import ProgressSpinner from "primevue/progressspinner";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import axios from "axios";

const store: any = inject("store");

const api: string = 'http://localhost:5100';

/**
 * ## toggled
 * When the fieldset is toggled, we need to update the state.
 * @param {any} e The toggle event
 */
const toggled = (e: any) => {
  store.state.schemas.open = !e.value;

  // If there's no data make the request to the api.
  if (store.state.schemas.open && !store.state.schemas.data) {

    // I still can't add schemas locally.. So....
    // Activate this url for the Sprint Demo.
    // const url = `/test_schemas.json`;

    const url = `${api}/tenant/v1/governance/schema_templates?page_size=1000`;

    axios
      .get(url, {
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${store.state.token}`,
        },
      })
      .then((res) => {
        store.state.schemas.data = res.data.items;
        console.log(store.state.schemas.data);
      })
      .catch((err) => {
        store.state.schemas.data = null;
        console.error("error", err);
      });
  }
};
</script>

<template>
  <Fieldset
    :toggleable="true"
    :collapsed="!store.state.schemas.open"
    @toggle="toggled"
  >
    <template #legend>Schemas</template>
    <ProgressSpinner v-if="!store.state.schemas.data" />
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
      <Button class="create-btn" icon="pi pi-plus" label="Create Schema" />
    </div>
  </Fieldset>
</template>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}
.create-btn {
  float: right;
  margin-top: 10px;
}
.p-datatable-header input {
  padding-left: 3rem;
}
</style>
