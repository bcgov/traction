<template>
  <h3 class="mt-0">{{ t('issue.credentials') }}</h3>

  <DataTable
    v-model:selection="selectedCredential"
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="credentials"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    selection-mode="single"
    data-key="issuer_credential_id"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <OfferCredential />
        </div>
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
          ></Button>
        </div>
      </div>
    </template>
    <template #empty> No records found. </template>
    <template #loading> Loading data. Please wait... </template>
    <Column :expander="true" header-style="width: 3rem" />
    <!-- <Column header="Actions">
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
    </Column> -->
    <Column
      :sortable="true"
      field="credential_definition_id"
      header="Credential Definition"
    />
    <Column :sortable="true" field="connection_id" header="Contact">
      <template #body="{ data }">
        {{ findConnectionName(data.connection_id) }}
      </template>
    </Column>
    <Column :sortable="true" field="state" header="Status">
      <template #body="{ data }">
        <StatusChip :status="data.state" />
      </template>
    </Column>
    <Column :sortable="true" field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData
        :id="data.credential_exchange_id"
        :url="API_PATH.ISSUE_CREDENTIALS_RECORDS"
      />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// State
import { useIssuerStore, useContactsStore } from '@/store';
import { storeToRefs } from 'pinia';
// PrimeVue/etc
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'vue-toastification';
import { useConfirm } from 'primevue/useconfirm';
import { useI18n } from 'vue-i18n';
// Other Components
import OfferCredential from './offerCredential/OfferCredential.vue';
import RowExpandData from '../common/RowExpandData.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';
import StatusChip from '../common/StatusChip.vue';

const toast = useToast();
const confirm = useConfirm();
const { t } = useI18n();

const contactsStore = useContactsStore();
const { contacts } = storeToRefs(useContactsStore());
const issuerStore = useIssuerStore();
// use the loading state from the store to disable the button...
const { loading, credentials, selectedCredential } = storeToRefs(
  useIssuerStore()
);

// Delete a specific cred
// const deleteCredential = (event: any, data: any) => {
//   confirm.require({
//     target: event.currentTarget,
//     message: 'Are you sure you want to DELETE this credential?',
//     header: 'Confirmation',
//     icon: 'pi pi-exclamation-triangle',
//     accept: () => {
//       issuerStore
//         .deleteCredential(data.issuer_credential_id)
//         .then(() => {
//           toast.success(`Credential deleted`);
//         })
//         .catch((err) => {
//           console.error(err);
//           toast.error(`Failure: ${err}`);
//         });
//     },
//   });
// };

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

  // Load contacts if not already there for display
  if (!contacts.value || !contacts.value.length) {
    contactsStore.listContacts().catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
};
onMounted(async () => {
  await loadTable();
});
// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

const filter = ref({
  alias: { value: null, matchMode: FilterMatchMode.CONTAINS },
});

// Find the connection alias for an ID
const findConnectionName = (connectionId: string) => {
  const connection = contacts.value?.find((c: any) => {
    return c.connection_id === connectionId;
  });
  return connection ? connection.alias : '...';
};
</script>

<style scoped>
.credential-search {
  margin-left: 1.5rem;
}
.credential-search input {
  padding-left: 3rem !important;
  margin-right: 1rem;
}
</style>
