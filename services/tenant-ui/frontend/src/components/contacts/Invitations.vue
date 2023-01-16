<template>
  <h3 class="mt-0">{{ t('connect.invitations.invitations') }}</h3>

  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="filteredInvitations"
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
          <CreateContact :multi="false" class="mr-3" />
          <CreateContact :multi="true" />
        </div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left mr-3">
            <i class="pi pi-search ml-0" />
            <InputText
              v-model="filter.alias.value"
              placeholder="Search Invitations"
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
        <DeleteContact :connection-id="data.connection_id" />
        <RegenerateInvitation :connection-id="data.connection_id" />
      </template>
    </Column>
    <Column :sortable="true" field="alias" header="Alias" />
    <Column :sortable="true" field="invitation_mode" header="Invitation Mode" />
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
import { useToast } from 'vue-toastification';
import { FilterMatchMode } from 'primevue/api';
// State
import { useContactsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import CreateContact from '@/components/contacts/createContact/CreateContact.vue';
import DeleteContact from '@/components/contacts/editContact/DeleteContact.vue';
import RegenerateInvitation from '@/components/contacts/createContact/RegenerateInvitation.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';
import { useI18n } from 'vue-i18n';

const toast = useToast();
const { t } = useI18n();

const contactsStore = useContactsStore();

const { loading, filteredInvitations } = storeToRefs(useContactsStore());

const loadTable = async () => {
  contactsStore.listContacts().catch((err) => {
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
