<template>
  <h3 class="mt-0">Credentials</h3>
  <DataTable
    v-model:selection="selectedCredential"
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="localTableCredentials"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['cred_def_id']"
    selection-mode="single"
    data-key="randomId"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start"></div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left credential-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.cred_def_id.value"
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
      <CredentialAttributes :attributes="data.attrs" />
    </template>
    <Column :expander="true" header-style="width: 3rem" />
    <!-- <Column header="Actions" class="action-col">
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
    </Column> -->
    <Column :sortable="true" field="cred_def_id" header="Credential" />
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { computed, onMounted, ref } from 'vue';
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
// Other components
import CredentialAttributes from './CredentialAttributes.vue';
import { TABLE_OPT } from '@/helpers/constants';

const toast = useToast();
const confirm = useConfirm();

const holderStore = useHolderStore();
// use the loading state from the store to disable the button...
const { loading, credentials, selectedCredential } = storeToRefs(
  useHolderStore()
);

// const acceptOffer = (event: any, data: any) => {
//   holderStore.acceptCredentialOffer(data.holder_credential_id).then(() => {
//     toast.success(`Credential successfully added to your wallet`);
//   });
// };
// const rejectOffer = (event: any, data: any) => {
//   holderStore.rejectCredentialOffer(data.holder_credential_id).then(() => {
//     toast.success(`Credential offer rejected`);
//   });
// };

// const deleteCredential = (event: any, data: any) => {
//   confirm.require({
//     target: event.currentTarget,
//     message: 'Are you sure you want to delete this credential?',
//     header: 'Confirmation',
//     icon: 'pi pi-exclamation-triangle',
//     accept: () => {
//       holderStore.deleteHolderCredential(data.holder_credential_id).then(() => {
//         loadTable();
//       });
//     },
//   });
// };

// Get the credential list when loading the component
const loadTable = async () => {
  holderStore.listCredentials().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});

// Add a random UD for the table data key
// since credentils aca-py response has no identifier per item
const localTableCredentials = computed(() => {
  return credentials.value.map((c) => ({
    ...c,
    randomId: (Math.random() + 1).toString(36).substring(3),
  }));
});

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

const filter = ref({
  cred_def_id: { value: null, matchMode: FilterMatchMode.CONTAINS },
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
