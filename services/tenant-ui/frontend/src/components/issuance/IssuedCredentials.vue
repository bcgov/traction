<template>
  <h3 class="mt-0">Issued/Offered Credentials</h3>

  <DataTable
    v-model:selection="selectedCredential"
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="credentials"
    :paginator="true"
    :rows="10"
    selection-mode="single"
    data-key="issuer_credential_id"
  >
    <template #header>
      <div class="flex justify-content-between">
        <OfferCredential />
        <Button
          icon="pi pi-refresh"
          class="p-button-rounded p-button-outlined"
          title="Refresh Table"
          @click="loadTable"
        ></Button>
      </div>
    </template>
    <template #empty> No records found. </template>
    <template #loading> Loading data. Please wait... </template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column
      :sortable="true"
      field="credential_template.name"
      header="Credential Name"
    />
    <Column field="contact.alias" header="Contact Name" />
    <Column field="status" header="Status" />
    <Column field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <Column field="revoked" header="Revoked?" />
    <template #expansion="{ data }">
      <IssuedCredentialRowExpandData :row="data" />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';

// State
import { useIssuerStore } from '../../store';
import { storeToRefs } from 'pinia';

// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';

// Other Components
import OfferCredential from './offerCredential/OfferCredential.vue';
import IssuedCredentialRowExpandData from './IssuedCredentialRowExpandData.vue';
import { formatDateLong } from '@/helpers';

// Other Imports
import { useToast } from 'vue-toastification';

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
// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);
</script>
