<template>
  <h3 class="mt-0">{{ $t('messages.messages') }}</h3>
  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:selection="selectedMessage"
    v-model:filters="filter"
    :loading="loading"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    :value="formattedMessages"
    :global-filter-fields="['content']"
    selection-mode="single"
    data-key="message_id"
    filterDisplay="menu"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <CreateMessage @success="loadTable" />
        </div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left message-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.content.value"
              placeholder="Search Messages"
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
    <template #empty>{{ $t('common.noRecordsFound') }}</template>
    <template #loading>{{ $t('common.loading') }}</template>
    <Column sortable field="contact" header="Contact" filter-field="contact">
      <template #body="{ data }">
        {{ data.contact }}
      </template>
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
    <Column :sortable="true" field="state" header="State" filter-field="state">
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
      field="content"
      header="Content"
      filter-field="content"
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
      field="created_at"
      header="Sent"
      filter-field="created_at"
    >
      <template #body="{ data }">
        {{ data.created_at }}
      </template>
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
  </DataTable>
</template>
<script setup lang="ts">
// Vue
import { onMounted, ref, Ref, computed } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
import { FilterMatchMode } from 'primevue/api';
// State
import { useMessageStore, useContactsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import { TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';
import CreateMessage from './createMessage/CreateMessage.vue';
import { BasicMessageRecord } from '@/types/acapyApi/acapyInterface';

const toast = useToast();

const messageStore = useMessageStore();
const contactsStore = useContactsStore();

const { loading, messages, selectedMessage } = storeToRefs(useMessageStore());
const { contacts } = storeToRefs(useContactsStore());

// Find the connection alias for an ID
const findConnectionName = (connectionId: string) => {
  const connection = contacts.value?.find((c: any) => {
    return c.connection_id === connectionId;
  });
  return connection ? connection.alias : '...';
};

const loadTable = async () => {
  // should return latest message first
  messageStore.listMessages().catch((err: any) => {
    toast.error(`Failure: ${err}`);
  });
  // messages = messages.map()
  // Load contacts if not already there for display
  if (!contacts.value || !contacts.value.length) {
    contactsStore.listContacts().catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
};
const expandedRows = ref([]);
interface FilteredMessage {
  connection_id: string | undefined;
  contact: string | undefined;
  state: string | undefined;
  content: string | undefined;
  sent_time: string | undefined;
  created_at: string | undefined;
}
const formattedMessages: Ref<FilteredMessage[]> = computed(() =>
  messages.value.map((msg: BasicMessageRecord) => ({
    connection_id: msg.connection_id,
    contact: findConnectionName(msg.connection_id ?? ''),
    state: msg.state,
    content: msg.content,
    sent_time: msg.sent_time,
    created_at: formatDateLong(msg.created_at ?? ''),
  }))
);
const filter = ref({
  content: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  cred_def_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  contact: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  credential_definition_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  state: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  created_at: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});
onMounted(() => {
  loadTable();
});
</script>

<style>
.message-search {
  margin-right: 1.5rem;
}
.message-search input {
  padding-left: 3rem !important;
}
</style>
