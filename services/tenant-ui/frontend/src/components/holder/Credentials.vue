<template>
  <h3 class="mt-0">Credentials</h3>

  <DataTable
    v-model:selection="selectedCredential"
    :loading="loading"
    :value="credentials"
    :paginator="true"
    :rows="10"
    striped-rows
    selection-mode="single"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start"></div>
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
    <template #empty> No records found. </template>
    <template #loading> Loading data. Please wait... </template>
    <Column :sortable="true" field="alias" header="Name" />
    <Column field="state" header="State" />
    <Column field="status" header="Status" />
    <Column field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <Column field="contact.alias" header="Contact Name" />
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useToast } from 'vue-toastification';

import { useHolderStore } from '../../store';
import { storeToRefs } from 'pinia';

import { formatDateLong } from '@/helpers';

const toast = useToast();

const holderStore = useHolderStore();
// use the loading state from the store to disable the button...
const { loading, credentials, selectedCredential } = storeToRefs(
  useHolderStore()
);

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
<style scoped>
.p-datatable-header input {
  padding-left: 3rem;
}
</style>
