<template>
  <h3 class="mt-0">My Held Credentials</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable :value="store.state.holderCredentials.data" :paginator="true" :rows="10" striped-rows
      v-model:selection="store.state.holderCredentials.selection" selection-mode="single">
      <Column :sortable="true" field="alias" header="Name" />
      <Column field="state" header="State" />
      <Column field="status" header="Status" />
      <Column field="created_at" header="Created at" />
      <Column field="contact.alias" header="Contact Name" />
    </DataTable>
  </div>
</template>


<script setup lang="ts">
// Vue
import { inject, ref, onMounted } from "vue";

// PrimeVue
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import ProgressSpinner from "primevue/progressspinner";

// Other imports
import axios from "axios";

// Store
const store: any = inject("store");

// ----------------------------------------------------------------
// Loading Creds
// ----------------------------------------------------------------
let loading = ref(true);

onMounted(() => {
  loading.value = true
  axios
    .get('/api/traction/tenant/v1/holder/credentials', {
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${store.state.token}`,
      },
    })
    .then((res) => {
      store.state.holderCredentials.data = res.data.items;
      console.log(store.state.holderCredentials.data);
      loading.value = false;
    })
    .catch((err) => {
      store.state.holderCredentials.data = null;
      console.error("error", err);
    });
})
// -----------------------------------------------/Loading creds

</script>
