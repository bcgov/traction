<template>
  <h3 class="mt-0">{{ t('contact.contacts') }}</h3>

  <DataTable
    v-model:selection="selectedContact"
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="contacts"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['alias']"
    selection-mode="single"
    data-key="alias"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <CreateContact />
          <AcceptInvitation class="ml-4" />
          <span class="p-input-icon-left contact-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.alias.value"
              placeholder="Search Contacts"
            />
          </span>
        </div>
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
    <Column :sortable="false" header="Actions">
      <template #body="{ data }">
        <Button
          title="Delete Contact"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="deleteContact($event, data)"
        />
        <EditContact :contact-id="data.contact_id" />
      </template>
    </Column>
    <Column :sortable="true" field="alias" header="Name" />
    <Column :sortable="true" field="role" header="Role" />
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
    <template #expansion="{ data }">
      <RowExpandData
        :id="data.contact_id"
        :url="API_PATH.CONTACTS"
        :params="{ acapy: true }"
      />
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
import { useContactsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import AcceptInvitation from './acceptInvitation/AcceptInvitation.vue';
import CreateContact from './createContact/CreateContact.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';
import RowExpandData from '../common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';
import EditContact from './editContact/EditContact.vue';
import { useI18n } from 'vue-i18n';
import { allowedNodeEnvironmentFlags } from 'process';

const confirm = useConfirm();
const toast = useToast();
const { t } = useI18n();

const contactsStore = useContactsStore();

const { loading, contacts, selectedContact } = storeToRefs(useContactsStore());

const loadTable = async () => {
  contactsStore.listContacts().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});

const deleteContact = (event: any, schema: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this contact?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete(schema);
    },
  });
};
const doDelete = (schema: any) => {
  contactsStore
    .deleteContact(schema)
    .then(() => {
      toast.success(`Contact successfully deleted`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
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
}
.contact-search {
  margin-left: 1.5rem;
}
</style>
