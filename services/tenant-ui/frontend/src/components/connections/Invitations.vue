<template>
  <MainCardContent
    :title="$t('connect.invitations.invitations')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:expanded-rows="expandedRows"
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
      filter-display="menu"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div class="flex justify-content-start">
            <CreateConnection />
          </div>
          <div class="flex justify-content-end">
            <IconField icon-position="left">
              <InputIcon><i class="pi pi-search" /></InputIcon>
              <InputText
                v-model="filter.alias.value"
                :placeholder="$t('connect.invitations.search')"
              />
            </IconField>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column :sortable="false" :header="$t('common.actions')">
        <template #body="{ data }">
          <DeleteConnection :connection-id="data.connection_id" />
          <RegenerateInvitation :connection-id="data.connection_id" />
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
        field="invitation_mode"
        :header="$t('connect.table.invitationMode')"
        filter-field="invitation_mode"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Invitation Mode"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="protocol"
        :header="$t('common.protocol')"
        filter-field="protocol"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Protocol"
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
      </template>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, computed } from 'vue';
// PrimeVue
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import DataTable from 'primevue/datatable';
import InputIcon from 'primevue/inputicon';
import IconField from 'primevue/iconfield';

import { useToast } from 'vue-toastification';
import { FilterMatchMode } from 'primevue/api';
// State
import { useConnectionStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import CreateConnection from '@/components/connections/createConnection/CreateConnection.vue';
import DeleteConnection from '@/components/connections/editConnection/DeleteConnection.vue';
import MainCardContent from '../layout/mainCard/MainCardContent.vue';
import RegenerateInvitation from '@/components/connections/createConnection/RegenerateInvitation.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const toast = useToast();

const connectionStore = useConnectionStore();

const { loading, filteredInvitations } = storeToRefs(useConnectionStore());

const formattedInvitations = computed(() =>
  filteredInvitations.value.map((inv) => ({
    connection_id: inv.connection_id,
    alias: inv.alias,
    invitation_mode: inv.invitation_mode,
    protocol: inv.connection_protocol,
    created: formatDateLong(inv.created_at as string),
    created_at: inv.created_at,
  }))
);
const loadTable = async () => {
  connectionStore.listConnections().catch((err) => {
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
  },
  invitation_mode: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  protocol: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});
</script>
