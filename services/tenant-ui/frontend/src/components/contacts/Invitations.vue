<template>
  <h3 class="mt-0">{{ $t('connect.invitations.invitations') }}</h3>

  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="formattedInvitations"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :global-filter-fields="['alias']"
    selection-mode="single"
    data-key="connection_id"
    sort-field="created_at"
    :sort-order="-1"
    filterDisplay="menu"
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
              :placeholder="$t('connect.invitations.search')"
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
        <DeleteContact :connection-id="data.connection_id" />
        <RegenerateInvitation :connection-id="data.connection_id" />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="alias"
      :header="$t('common.alias')"
      filterField="alias"
    >
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          @input="filterCallback()"
          class="p-column-filter"
          placeholder="Search By Alias"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="invitation_mode"
      :header="$t('connect.table.invitationMode')"
      filterField="invitation_mode"
    >
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          @input="filterCallback()"
          class="p-column-filter"
          placeholder="Search By Invitation Mode"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="created"
      :header="$t('connect.table.createdAt')"
      filterField="created"
    >
      <template #body="{ data }">
        {{ data.created }}
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <InputText
          v-model="filterModel.value"
          type="text"
          @input="filterCallback()"
          class="p-column-filter"
          placeholder="Search By Date"
        />
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData :id="data.connection_id" :url="API_PATH.CONNECTIONS" />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, Ref, computed } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
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

const toast = useToast();

const contactsStore = useContactsStore();

const { loading, filteredInvitations } = storeToRefs(useContactsStore());

const formattedInvitations = computed(() =>
  filteredInvitations.value.map((inv) => ({
    alias: inv.alias,
    invitation_mode: inv.invitation_mode,
    created: formatDateLong(inv.created_at as string),
    created_at: inv.created_at,
  }))
);
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
  alias: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  invitation_mode: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
});
</script>
