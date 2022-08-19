<template>
  <h3 class="mt-0">My Held Credentials</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable v-model:selection="selectedCredential" :value="credentials" :paginator="true" :rows="10" striped-rows selection-mode="single">
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
import { onMounted } from 'vue';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import ProgressSpinner from 'primevue/progressspinner';
import { useToast } from 'vue-toastification';

import { useHolderStore } from '../../store';
import { storeToRefs } from 'pinia';

const toast = useToast();

const holderStore = useHolderStore();
// use the loading state from the store to disable the button...
const { loading, credentials, selectedCredential } = storeToRefs(useHolderStore());

const loadTable = async () => {
  holderStore.listCredentials().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});
</script>
