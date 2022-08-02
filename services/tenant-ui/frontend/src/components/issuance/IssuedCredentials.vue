<template>
  <h3 class="mt-0">My Issued Credentials</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable :value="store.state.issuerCredentials.data" :paginator="true" :rows="10" striped-rows
      v-model:selection="store.state.issuerCredentials.selection" selection-mode="single">
      <Column :sortable="true" field="credential_template.name" header="Credential Name" />
      <Column field="contact.alias" header="Contact Name" />
      <Column field="state" header="State" />
      <Column field="status" header="Status" />
      <Column field="created_at" header="Created at" />
      <Column field="issuer_credential_id" header="ID" />
      <Column field="revoked" header="Revoked?" />
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
// Loading creds
// ----------------------------------------------------------------
let loading = ref(true);

onMounted(() => {
  loading.value = true

  axios
    .get('/api/traction/tenant/v1/issuer/credentials', {
      headers: {
        accept: "application/json",
        Authorization: `Bearer ${store.state.token}`,
      },
    })
    .then((res) => {
      store.state.issuerCredentials.data = res.data.items;
      console.log(store.state.issuerCredentials.data);
      loading.value = false;
    })
    .catch((err) => {
      store.state.issuerCredentials.data = null;
      console.error("error", err);
    });
})
// -------------------------------------------------/Loading creds
</script>
