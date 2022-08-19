<template>
  <h3 class="mt-0">My Issued Credentials</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable
      v-model:selection="selectedCredential"
      :value="credentials"
      :paginator="true"
      :rows="10"
      striped-rows
      selection-mode="single"
    >
      <Column
        :sortable="true"
        field="credential_template.name"
        header="Credential Name"
      />
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
import { onMounted } from "vue";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import ProgressSpinner from "primevue/progressspinner";
import { useToast } from "vue-toastification";

import { useIssuerStore } from "../../store";
import { storeToRefs } from "pinia";

const toast = useToast();

const issuerStore = useIssuerStore();
// use the loading state from the store to disable the button...
const { loading, credentials, selectedCredential } = storeToRefs(
  useIssuerStore()
);

const loadTable = async () => {
  await issuerStore.listCredentials().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  await loadTable();
});
</script>
