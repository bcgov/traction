<template>
  <h3 class="mt-0">{{ $t('credentials.credentials') }}</h3>
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
    sort-field="updated_at"
    :sort-order="-1"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start"></div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left credential-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.cred_def_id.value"
              :placeholder="$t('credentials.search')"
            />
          </span>
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-button-outlined"
            :title="$t('credentials.table.refresh')"
            @click="loadTable"
          />
        </div>
      </div>
    </template>
    <template #empty>{{ $t('credentials.table.noRecords') }}</template>
    <template #loading>{{ $t('credentials.table.loading') }}</template>
    <template #expansion="{ data }">
      <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
      <CredentialAttributes :attributes="getAttributes(data)" />
      --
      <RowExpandData
        :id="data.credential_exchange_id"
        :url="API_PATH.ISSUE_CREDENTIAL_RECORDS"
      />
    </template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column :header="$t('credentials.table.actions')" class="action-col">
      <template #body="{ data }">
        <Button
          title="Accept Credential into Wallet"
          icon="pi pi-check"
          class="p-button-rounded p-button-icon-only p-button-text"
          :class="{ accepted: data.state === 'credential_acked' }"
          :disabled="data.state !== 'offer_received'"
          @click="acceptOffer($event, data)"
        />
        <Button
          title="Reject Credential Offer"
          icon="pi pi-times"
          class="p-button-rounded p-button-icon-only p-button-text"
          :disabled="data.state !== 'offer_received'"
          @click="rejectOffer($event, data)"
        />
        <Button
          title="Delete Credential Exchange Record"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          :disabled="data.state === 'offer_received'"
          @click="deleteCredential($event, data)"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="connection_id"
      :header="$t('credentials.table.connection')"
    >
      <template #body="{ data }">
        {{ findConnectionName(data.connection_id) }}
      </template>
    </Column>
    <Column
      :sortable="true"
      field="credential_definition_id"
      :header="$t('credentials.table.credential')"
    />
    <Column :sortable="true" field="state" header="Status">
      <template #body="{ data }">
        <StatusChip :status="data.state" />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="updated_at"
      :header="$t('credentials.table.lastUpdate')"
    >
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
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
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
  return data.credential_offer_dict?.credential_preview?.attributes ?? [];
};

// Actions for a cred row
const acceptOffer = (event: any, data: V10CredentialExchange) => {
  if (data.credential_exchange_id) {
    holderStore.acceptCredentialOffer(data.credential_exchange_id).then(() => {
      toast.success(`Credential successfully added to your wallet`);
    });
  }
};
const rejectOffer = (event: any, data: V10CredentialExchange) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to reject this credential offer?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      if (data.credential_exchange_id) {
        holderStore
          .deleteCredentialExchange(data.credential_exchange_id)
          .then(() => {
            loadTable();
            toast.success(`Credential offer rejected`);
          });
      }
    },
  });
};

const deleteCredential = (event: any, data: V10CredentialExchange) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this credential exchange record?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      if (data.credential_exchange_id) {
        holderStore
          .deleteCredentialExchange(data.credential_exchange_id)
          .then(() => {
            loadTable();
            toast.info(`Credential exchange deleted`);
          });
      }
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
  cred_def_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
});
</script>
<style scoped>
.p-datatable-header input {
  padding-left: 3rem;
  margin-right: 1rem;
}
button.accepted {
  color: green !important;
}
</style>
