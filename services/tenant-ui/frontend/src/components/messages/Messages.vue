<template>
  <MainCardContent
    :title="$t('messages.messages')"
    :refresh-callback="loadTable"
  >
    <p class="pt-0">
      <i class="pi pi-info-circle mr-1"></i>
      {{ $t('messages.disclaimer') }}
    </p>
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
              v-if="
                stringOrBooleanTruthy(config.frontend.showWritableComponents)
              "
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
        field="connection"
        header="Connection"
        filter-field="connection"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <LoadingLabel :value="data.connection" />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Connection"
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
import { computed, onMounted, ref } from 'vue';
// PrimeVue
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
// State
import { useConnectionStore, useMessageStore } from '@/store';
import { Message } from '@/store/messageStore';
import { storeToRefs } from 'pinia';
// Other components
import { formatDateLong, stringOrBooleanTruthy } from '@/helpers';
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
const { listConnections, findConnectionName } = useConnectionStore();

const { loading, messages, selectedMessage } = storeToRefs(useMessageStore());
const { connections } = storeToRefs(useConnectionStore());

const loadTable = async () => {
  // should return latest message first
  messageStore.listMessages().catch((err: any) => {
    toast.error(`Failure: ${err}`);
  });

  // Load connections if not already there for display
  if (!connections.value || !connections.value.length) {
    listConnections().catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
};
const expandedRows = ref([]);
const formattedMessages = computed(() =>
  messages.value.map((msg: Message) => ({
    message_id: msg.message_id,
    connection_id: msg.connection_id,
    connection: findConnectionName(msg.connection_id),
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
  connection: {
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
