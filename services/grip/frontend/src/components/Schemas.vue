<script setup lang="ts">
import { inject } from "vue";
import Fieldset from "primevue/fieldset";
import Button from "primevue/button";
import ProgressSpinner from "primevue/progressspinner";
import DataTable from "primevue/datatable";
import axios from "axios";

const store: any = inject("store");

// Vite passes the api url to here
const api = import.meta.env.VITE_TRACTION_ENDPOINT;

/**
 * ## toggled
 * When the fieldset is toggled, we need to update the state.
 * @param {any} e The toggle event
 */
const toggled = (e: any) => {
  store.state.schemas.open = !e.value;

  // If there's no data make the request to the api.
  if (store.state.schemas.open && !store.state.schemas.data) {
    axios
      .get(`${api}/tenant/v1/governance/schema_templates?page_size=1000`, {
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${store.state.token}`,
        },
      })
      .then((res) => {
        store.state.schemas.data = res.data.items;
        console.log(res.data.items);
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
      <!-- <DataTable></DataTable> -->
      Here is some text
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
</style>
