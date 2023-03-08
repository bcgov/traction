<template>
  <h3 class="mt-0">Credentials</h3>
  <DataTable
    v-model:selection="selectedCredential"
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="credentialExchanges"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['cred_def_id']"
    selection-mode="single"
    data-key="credential_exchange_id"
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
      <CredentialAttributes :attributes="getAttributes(data)" />
      --
      <RowExpandData
        :id="data.credential_exchange_id"
        :url="API_PATH.ISSUE_CREDENTIAL_RECORDS"
      />
    </template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column header="Actions" class="action-col">
      <template #body="{ data }">
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
        <Button
          title="Delete Credential"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="deleteCredential($event, data)"
        />
      </template>
    </Column>
    <Column :sortable="true" field="connection_id" header="Connection">
      <template #body="{ data }">
        {{ findConnectionName(data.connection_id) }}
      </template>
    </Column>
    <Column
      :sortable="true"
      field="credential_definition_id"
      header="Credential"
    />
    <Column :sortable="true" field="state" header="Status">
      <template #body="{ data }">
        <StatusChip :status="data.state" />
      </template>
    </Column>
    <Column :sortable="true" field="updatedAt" header="Last update">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
  </DataTable>
</template>

<script setup lang="ts">
// Types
import {
  CredAttrSpec,
  V10CredentialExchange,
} from '@/types/acapyApi/acapyInterface';

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
import { useContactsStore, useHolderStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import CredentialAttributes from './CredentialAttributes.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const toast = useToast();
const confirm = useConfirm();

// State
const contactsStore = useContactsStore();
const { contacts } = storeToRefs(useContactsStore());
const holderStore = useHolderStore();
const { loading, credentialExchanges, selectedCredential } = storeToRefs(
  useHolderStore()
);

const getAttributes = (data: V10CredentialExchange): CredAttrSpec[] => {
  let attrs = [] as CredAttrSpec[];
  if ((data.state = 'offer_received')) {
    attrs = data.credential_offer_dict?.credential_preview?.attributes ?? [];
  }
  return attrs;
};

// Actions for a cred row
const acceptOffer = (event: any, data: any) => {
  holderStore.acceptCredentialOffer(data.holder_credential_id).then(() => {
    toast.success(`Credential successfully added to your wallet`);
  });
};
const rejectOffer = (event: any, data: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to reject this credential offer?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      holderStore.rejectCredentialOffer(data.holder_credential_id).then(() => {
        loadTable();
        toast.success(`Credential offer rejected`);
      });
    },
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
        toast.info(`Credential offer rejected`);
      });
    },
  });
};

// Get the credential exchange list when loading the component
const loadTable = async () => {
  holderStore.listHolderCredentialExchanges().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });

  // Load contacts if not already there for display
  if (!contacts.value || !contacts.value.length) {
    contactsStore.listContacts().catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
};

onMounted(async () => {
  loadTable();
});

// Add a random UD for the table data key
// since credentils aca-py response has no identifier per item
// const localTableCredentials = computed(() => {
//   return credentials.value.map((c) => ({
//     ...c,
//     randomId: (Math.random() + 1).toString(36).substring(3),
//   }));
// });

// Find the connection alias for an ID
const findConnectionName = (connectionId: string) => {
  const connection = contacts.value?.find((c: any) => {
    return c.connection_id === connectionId;
  });
  return connection ? connection.alias : '...';
};

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
</style>
