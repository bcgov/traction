<template>
  <h3 class="mt-0">Credentials</h3>

  <DataTable
    v-model:selection="selectedCredential"
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="credentials"
    :paginator="true"
    :rows="10"
    selection-mode="single"
    data-key="holder_credential_id"
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
    <Column :expander="true" header-style="width: 3rem" />
    <Column :sortable="true" field="alias" header="Name" />
    <Column field="status" header="Status" />
    <Column field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <Column field="contact.alias" header="Contact Name" />
    <template #expansion="{ data }">
      <CredentialRowExpandData :row="data" />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useToast } from 'vue-toastification';

import { useHolderStore } from '../../store';
import { storeToRefs } from 'pinia';
import CredentialRowExpandData from './CredentialRowExpandData.vue';

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
// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);
</script>
<style scoped>
.p-datatable-header input {
  padding-left: 3rem;
}
</style>
