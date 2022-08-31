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
      <Column
        :sortable="true"
        field="credential_template.name"
        header="Credential Name"
      />
      <Column field="contact.alias" header="Contact Name" />
      <Column field="state" header="State" />
      <Column field="status" header="Status" />
      <Column field="created_at" header="Created at">
        <template #body="{ data }">
          123 {{  data.created_at  }}
        </template>
      </Column>
      <Column field="issuer_credential_id" header="ID" />
      <Column field="revoked" header="Revoked?" />
    </DataTable>
  </div>
</template>

<script setup lang="ts">
// Vue
import { onMounted } from 'vue';

// State
import { useIssuerStore } from '../../store';
import { storeToRefs } from 'pinia';

// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import ProgressSpinner from 'primevue/progressspinner';

// Other Components
import OfferCredential from './offerCredential/OfferCredential.vue';

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
</script>
