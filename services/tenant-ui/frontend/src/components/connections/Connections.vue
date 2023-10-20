<template>
  <MainCardContent
    :title="$t('connect.connections.connections')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:expandedRows="expandedRows"
      v-model:filters="filter"
      :loading="loading"
      :value="formattedConnections"
      :paginator="true"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      :global-filter-fields="['alias']"
      selection-mode="single"
      data-key="connection_id"
      sort-field="created_at"
      :sort-order="-1"
      filter-display="menu"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div class="flex justify-content-start">
            <AcceptInvitation />
            <DidExchange class="ml-4" />
          </div>
          <div class="flex justify-content-end">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText
                v-model="filter.alias.value"
                :placeholder="$t('connect.connections.search')"
              />
            </span>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column :sortable="false" :header="$t('common.actions')">
        <template #body="{ data }">
          <MessageConnection
            :connection-id="data.connection_id"
            :connection-name="data.alias"
          />
          <Button
            title="Delete Connection"
            icon="pi pi-trash"
            class="p-button-rounded p-button-icon-only p-button-text"
            :disabled="deleteDisabled(data.alias)"
            @click="deleteConnection($event, data.connection_id)"
          />
          <EditConnection :connection-id="data.connection_id" />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="alias"
        :header="$t('common.alias')"
        filter-field="alias"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Alias"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="their_label"
        filter-field="their_label"
        :header="$t('connect.table.theirLabel')"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Label"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="state"
        :header="$t('common.status')"
        filter-field="state"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <StatusChip :status="data.state" />
        </template>
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
        field="created"
        :header="$t('connect.table.createdAt')"
        filter-field="created"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          {{ data.created }}
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Date"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <template #expansion="{ data }">
        <RowExpandData :id="data.connection_id" :url="API_PATH.CONNECTIONS" />
        <hr class="expand-divider" />
        <RowExpandData
          :url="API_PATH.CONNECTIONS_ENDPOINTS(data.connection_id)"
          label="View Connection Endpoints"
        />
        <hr class="expand-divider" />
        <RowExpandData
          :url="API_PATH.CONNECTIONS_METADATA(data.connection_id)"
          label="View Connection Metadata"
        />
      </template>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, Ref, computed } from 'vue';
import { FilterMatchMode } from 'primevue/api';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useConnectionStore, useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import AcceptInvitation from './acceptInvitation/AcceptInvitation.vue';
import DidExchange from './didExchange/DidExchange.vue';
import EditConnection from './editConnection/EditConnection.vue';
import MainCardContent from '../layout/mainCard/MainCardContent.vue';
import MessageConnection from './messageConnection/MessageConnection.vue';
import RowExpandData from '../common/RowExpandData.vue';
import StatusChip from '../common/StatusChip.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const confirm = useConfirm();
const toast = useToast();

// State
const connectionStore = useConnectionStore();
const tenantStore = useTenantStore();

const { loading, filteredConnections } = storeToRefs(useConnectionStore());
const { endorserInfo } = storeToRefs(useTenantStore());

const loadTable = async () => {
  connectionStore.listConnections().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  // So we can check endorser connection
  tenantStore.getEndorserInfo();
  // Load your connection list
  loadTable();
});

// Deleting a connection
const deleteConnection = (event: any, id: string) => {
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
  connectionStore
    .deleteConnection(id)
    .then(() => {
      toast.success(`Connection successfully deleted`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};
// Can't delete if it's endorser
const deleteDisabled = (connectionAlias: string) => {
  return (
    endorserInfo.value != null &&
    endorserInfo.value.endorser_name === connectionAlias
  );
};

// The formatted table row
const formattedConnections: Ref<any[]> = computed(() =>
  filteredConnections.value.map((conn) => ({
    connection_id: conn.connection_id,
    alias: conn.alias,
    their_label: conn.their_label,
    state: conn.state,
    created: formatDateLong(conn.created_at as string),
    created_at: conn.created_at,
  }))
);
// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

const filter = ref({
  alias: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  their_label: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  state: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});
</script>
