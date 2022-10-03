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
    <Column header="Actions" class="action-col">
      <template #body="{ data }">
        <div v-if="data.state == 'offer_received'">
          <Button
            v-tooltip.top="'Accept Credential into Wallet'"
            label="Accept"
            class="p-button-success"
            icon="pi pi-id-card"
            @click="acceptOffer($event, data)"
          />
          <Button
            v-tooltip.top="'Report Issue with Credential'"
            label="Reject"
            class="p-button-secondary"
            icon="pi pi-times-circle"
            @click="rejectOffer($event, data)"
          />
        </div>
        <div v-else>
          <Button
            v-tooltip.top="'Delete Credential'"
            label="Delete"
            class="p-button-danger"
            icon="pi pi-times-circle"
            @click="deleteCredential($event, data)"
          />
        </div>
      </template>
    </Column>
    <Column :sortable="true" field="alias" header="Name" />
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
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useToast } from 'vue-toastification';

import { useHolderStore } from '../../store';
import { storeToRefs } from 'pinia';
import CredentialRowExpandData from './CredentialRowExpandData.vue';
import { useConfirm } from 'primevue/useconfirm';

import { formatDateLong } from '@/helpers';

const toast = useToast();
const confirm = useConfirm();

const holderStore = useHolderStore();
// use the loading state from the store to disable the button...
const { loading, credentials, selectedCredential } = storeToRefs(
  useHolderStore()
);

const acceptOffer = (event: any, data: any) => {
  holderStore.acceptCredentialOffer(data.holder_credential_id).then(() => {
    loadTable();
  });
};
const rejectOffer = (event: any, data: any) => {
  holderStore.rejectCredentialOffer(data.holder_credential_id).then(() => {
    loadTable();
  });
};

const deleteCredential = (event: any, data: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this credential?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      holderStore.deleteHolderCredential(data.holder_credential_id).then(() => {
        loadTable();
      });
    },
  });
};

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

.action-col Button {
  margin-right: 1rem;
}
</style>
