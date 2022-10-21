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
    <Column header="Actions">
      <template #body="{ data }">
        <Button
          title="Delete Credential"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text mr-2"
          @click="deleteCredential($event, data)"
        />
        <Button
          v-if="
            data.credential_template &&
            data.credential_template.revocation_enabled &&
            !data.revoked
          "
          title="Revoke Credential"
          icon="pi pi-times-circle"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="revokeCredential($event, data)"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="credential_template.name"
      header="Credential Name"
    />
    <Column field="contact.alias" header="Contact Name" />
    <Column field="status" header="Status">
      <template #body="{ data }">
        <StatusChip :status="data.status" />
      </template>
    </Column>
    <Column field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData
        :id="data.issuer_credential_id"
        :url="'/tenant/v1/issuer/credentials/'"
        :params="{ acapy: true }"
      />
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
import { useToast } from 'vue-toastification';
import { useConfirm } from 'primevue/useconfirm';
// Other Components
import OfferCredential from './offerCredential/OfferCredential.vue';
import RowExpandData from '../common/RowExpandData.vue';
import { formatDateLong } from '@/helpers';
import StatusChip from '../common/StatusChip.vue';

const toast = useToast();
const confirm = useConfirm();

const issuerStore = useIssuerStore();
// use the loading state from the store to disable the button...
const { loading, credentials, selectedCredential } = storeToRefs(
  useIssuerStore()
);

// Delete a specific cred
const deleteCredential = (event: any, data: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to DELETE this credential?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      issuerStore
        .deleteCredential(data.issuer_credential_id)
        .then(() => {
          toast.success(`Credential deleted`);
        })
        .catch((err) => {
          console.error(err);
          toast.error(`Failure: ${err}`);
        });
    },
  });
};

// Revoke a specific cred
const revokeCredential = (event: any, data: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to REVOKE this credential?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      issuerStore
        .revokeCredential({
          issuer_credential_id: data.issuer_credential_id,
        })
        .then(() => {
          toast.success(`Credential revoked`);
        })
        .catch((err) => {
          console.error(err);
          toast.error(`Failure: ${err}`);
        });
    },
  });
};

// Get the credentials
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
