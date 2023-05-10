<template>
  <h3 class="mt-0">{{ $t('connect.connections.connections') }}</h3>

  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="filteredConnections"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['alias']"
    selection-mode="single"
    data-key="connection_id"
    sort-field="created_at"
    :sort-order="-1"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <AcceptInvitation />
          <DidExchange class="ml-4" />
        </div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left contact-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.alias.value"
              :placeholder="$t('connect.connections.search')"
            />
          </span>
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-button-outlined"
            :title="$t('common.refreshTable')"
            @click="loadTable"
          />
        </div>
      </div>
    </template>
    <template #empty>{{ $t('common.noRecordsFound') }}</template>
    <template #loading>{{ $t('common.loading') }}</template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column :sortable="false" :header="$t('common.actions')">
      <template #body="{ data }">
        <MessageContact
          :connection-id="data.connection_id"
          :connection-name="data.alias"
        />
        <Button
          title="Delete Contact"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          :disabled="deleteDisabled(data.alias)"
          @click="deleteContact($event, data.connection_id)"
        />
        <EditContact :connection-id="data.connection_id" />
      </template>
    </Column>
    <Column :sortable="true" field="alias" :header="$t('common.alias')" />
    <Column
      :sortable="true"
      field="their_label"
      :header="$t('connect.table.theirLabel')"
    />
    <Column :sortable="true" field="status" :header="$t('common.status')">
      <template #body="{ data }">
        <StatusChip :status="data.state" />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="created_at"
      :header="$t('connect.table.createdAt')"
    >
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData :id="data.connection_id" :url="API_PATH.CONNECTIONS" />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useContactsStore, useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import AcceptInvitation from './acceptInvitation/AcceptInvitation.vue';
// import AcceptInvitation from './acceptInvitation/AcceptInvitation.vue';
import DidExchange from './didExchange/DidExchange.vue';
import EditContact from './editContact/EditContact.vue';
import MessageContact from './messageContact/MessageContact.vue';
import RowExpandData from '../common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const confirm = useConfirm();
const toast = useToast();

const contactsStore = useContactsStore();
const tenantStore = useTenantStore();

const { loading, filteredConnections } = storeToRefs(useContactsStore());
const { endorserInfo } = storeToRefs(useTenantStore());

const loadTable = async () => {
  contactsStore.listContacts().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  // So we can check endorser connection
  tenantStore.getEndorserInfo();
  // Load your contact list
  loadTable();
});

// Deleting a contact
const deleteContact = (event: any, id: string) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this connection?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete(id);
    },
  });
};
const doDelete = (id: string) => {
  contactsStore
    .deleteContact(id)
    .then(() => {
      toast.success(`Connection successfully deleted`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};
// Can't delete if it's endorser
const deleteDisabled = (contactAlias: string) => {
  return (
    endorserInfo.value != null &&
    endorserInfo.value.endorser_name === contactAlias
  );
};

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

const filter = ref({
  alias: { value: null, matchMode: 'contains' } as DataTableFilterMetaData,
});
</script>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}

.create-contact {
  float: right;
  margin: 3rem 1rem 0 0;
}
.p-datatable-header input {
  padding-left: 3rem;
  margin-right: 1rem;
}
.contact-search {
  margin-left: 1.5rem;
}
</style>
