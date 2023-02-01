<template>
  <h3 class="mt-0">{{ t('connect.connections') }}</h3>

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
          <!-- <AcceptInvitation class="ml-4" /> -->
        </div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left contact-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.alias.value"
              placeholder="Search Connections"
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
    <Column :expander="true" header-style="width: 3rem" />
    <Column :sortable="false" header="Actions">
      <template #body="{ data }">
        <Button
          title="Delete Contact"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          :disabled="deleteDisabled(data.alias)"
          @click="deleteContact($event, data.connection_id)"
        />
        <!-- <EditContact :contact-id="data.contact_id" /> -->
      </template>
    </Column>
    <Column :sortable="true" field="alias" header="Alias" />
    <Column :sortable="true" field="their_label" header="Their Label" />
    <Column :sortable="true" field="status" header="Status">
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
import DataTable from 'primevue/datatable';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
import { FilterMatchMode } from 'primevue/api';
// State
import { useContactsStore, useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
// import AcceptInvitation from './acceptInvitation/AcceptInvitation.vue';
// import EditContact from './editContact/EditContact.vue';
import RowExpandData from '../common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';
import { useI18n } from 'vue-i18n';

const confirm = useConfirm();
const toast = useToast();
const { t } = useI18n();

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
    endorserInfo.value && endorserInfo.value.endorser_name === contactAlias
  );
};

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

const filter = ref({
  alias: { value: null, matchMode: FilterMatchMode.CONTAINS },
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
