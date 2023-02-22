<template>
  <h3 class="mt-0">Credentials</h3>
  <DataTable
    v-model:selection="selectedCredential"
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="credentials"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    selection-mode="single"
    data-key="holder_credential_id"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start"></div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left credential-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.alias.value"
              placeholder="Search Credentials"
            />
          </span>
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
    <template #expansion="{ data }">
      <RowExpandData
        :id="data.holder_credential_id"
        :url="API_PATH.CREDENTIALS"
        :params="{ acapy: true }"
      />
    </template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column header="Actions" class="action-col">
      <template #body="{ data }">
        <div v-if="data.state == 'offer_received'">
          <Button
            title="Accept Credential into Wallet"
            icon="pi pi-check"
            class="p-button-rounded p-button-icon-only p-button-text"
            @click="acceptOffer($event, data)"
          />
          <Button
            title="Reject Credential Offer"
            icon="pi pi-times"
            class="p-button-rounded p-button-icon-only p-button-text"
            @click="rejectOffer($event, data)"
          />
        </div>
        <div v-else>
          <Button
            title="Delete Credential"
            icon="pi pi-trash"
            class="p-button-rounded p-button-icon-only p-button-text"
            @click="deleteCredential($event, data)"
          />
        </div>
      </template>
    </Column>
    <Column :sortable="true" field="alias" header="Name" />
    <Column :sortable="true" field="status" header="Status">
      <template #body="{ data }">
        <StatusChip :status="data.status" />
      </template>
    </Column>
    <Column :sortable="true" field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <Column :sortable="true" field="contact.alias" header="Contact Name" />
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useHolderStore } from '@/store';
import { storeToRefs } from 'pinia';
// Components
import RowExpandData from '@/common/RowExpandData.vue';
import StatusChip from '@/common/StatusChip.vue';

import { TABLE_OPT, API_PATH } from '@/helpers/constants';
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
    toast.success(`Credential successfully added to your wallet`);
  });
};
const rejectOffer = (event: any, data: any) => {
  holderStore.rejectCredentialOffer(data.holder_credential_id).then(() => {
    toast.success(`Credential offer rejected`);
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

const filter = ref({
  alias: { value: null, matchMode: FilterMatchMode.CONTAINS },
});
</script>
<style scoped>
.p-datatable-header input {
  padding-left: 3rem;
  margin-right: 1rem;
}

.action-col Button {
  margin-right: 1rem;
}
</style>
