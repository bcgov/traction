<template>
  <MainCardContent
    :title="$t('messages.messages')"
    :refresh-callback="loadTable"
  >
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
      filter-display="menu"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div class="flex justify-content-start">
            <CreateMessage
              v-if="config.frontend.showWritableComponents"
              @success="loadTable"
            />
          </div>
          <div class="flex justify-content-end">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText
                v-model="filter.content.value"
                placeholder="Search Messages"
              />
            </span>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column
        sortable
        field="contact"
        header="Contact"
        filter-field="contact"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <LoadingLabel :value="data.contact" />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Contact"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="state"
        header="State"
        filter-field="state"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By State"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="content"
        header="Content"
        filter-field="content"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Content"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="created_at"
        header="Sent"
        filter-field="created_at"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          {{ data.created_at }}
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Time"
            @input="filterCallback()"
          />
        </template>
      </Column>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
// Vue
import { Ref, computed, onMounted, ref } from 'vue';
// PrimeVue
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
// State
import { useContactsStore, useMessageStore } from '@/store';
import { Message } from '@/store/messageStore';
import { storeToRefs } from 'pinia';
// Other components
import { formatDateLong } from '@/helpers';
import { TABLE_OPT } from '@/helpers/constants';
import MainCardContent from '../layout/mainCard/MainCardContent.vue';
import CreateMessage from './createMessage/CreateMessage.vue';
import LoadingLabel from '../common/LoadingLabel.vue';

// State
import { useConfigStore } from '@/store/configStore';
const { config } = storeToRefs(useConfigStore());

console.log('config', config);

const toast = useToast();

const messageStore = useMessageStore();
const { listContacts, findConnectionName } = useContactsStore();

const { loading, messages, selectedMessage } = storeToRefs(useMessageStore());
const { contacts } = storeToRefs(useContactsStore());

const loadTable = async () => {
  // should return latest message first
  messageStore.listMessages().catch((err: any) => {
    toast.error(`Failure: ${err}`);
  });
  // messages = messages.map()
  // Load contacts if not already there for display
  if (!contacts.value || !contacts.value.length) {
    listContacts().catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
};
const expandedRows = ref([]);
interface FilteredMessage {
  connection_id: string;
  contact: string | undefined;
  state: string;
  content: string;
  sent_time: string;
  created_at: string;
}
const formattedMessages: Ref<FilteredMessage[]> = computed(() =>
  messages.value.map((msg: Message) => ({
    connection_id: msg.connection_id,
    contact: findConnectionName(msg.connection_id),
    state: msg.state,
    content: msg.content,
    sent_time: msg.sent_time,
    created_at: formatDateLong(msg.created_at),
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
  },
  contact: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  credential_definition_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  state: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  created_at: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});

onMounted(() => {
  loadTable();
});
</script>
