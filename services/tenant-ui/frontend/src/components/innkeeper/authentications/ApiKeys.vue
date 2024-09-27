<template>
  <MainCardContent :title="$t('apiKey.apiKeys')" :refresh-callback="loadTable">
    <DataTable
      v-model:expanded-rows="expandedRows"
      v-model:filters="filter"
      :loading="loading"
      :value="formattedApiKeys"
      :paginator="true"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      selection-mode="single"
      data-key="tenant_id"
      sort-field="created_at"
      :sort-order="-1"
      filter-display="menu"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div class="flex justify-content-start">
            <CreateApiKey @success="loadTable" />
          </div>
          <div class="flex justify-content-end">
            <span class="p-input-icon-left">
              <i class="pi pi-search ml-0" />
              <InputText
                v-model="filter.global.value"
                :placeholder="$t('apiKey.search')"
              />
            </span>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column header="Actions">
        <template #body="{ data }">
          <DeleteApiKey :record-id="data.tenant_authentication_api_id" />
        </template>
      </Column>
      <Column
        sortable
        field="name"
        header="Tenant Name"
        filter-field="name"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <LoadingLabel :value="data.name" />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Tenant Name"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="tenant_id"
        header="Tenant ID"
        filter-field="tenant_id"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Filter"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="alias"
        header="Alias"
        filter-field="alias"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Filter"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="created"
        header="Created at"
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
            placeholder="Filter"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <template #expansion="{ data }">
        <RowExpandData
          :id="data.tenant_authentication_api_id"
          :url="API_PATH.INNKEEPER_AUTHENTICATIONS_API"
        />
      </template>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, computed } from 'vue';
// PrimeVue
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'vue-toastification';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong, formatGuid } from '@/helpers';
import CreateApiKey from './createApiKey/CreateApiKey.vue';
import DeleteApiKey from './DeleteApiKey.vue';
import LoadingLabel from '@/components/common/LoadingLabel.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';

const toast = useToast();

const innkeeperTenantsStore = useInnkeeperTenantsStore();

// Populating the Table
const { findTenantName } = useInnkeeperTenantsStore();
const { loading, apiKeys, tenants } = storeToRefs(useInnkeeperTenantsStore());
const loadTable = async () => {
  innkeeperTenantsStore.listApiKeys().catch((err: string) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });

  // Load tenants if not already there for display
  if (!tenants.value || !tenants.value.length) {
    innkeeperTenantsStore.listTenants().catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
};

// Formatting the table row
const formattedApiKeys = computed(() =>
  apiKeys.value.map((api: any) => ({
    tenant_authentication_api_id: formatGuid(api.tenant_authentication_api_id),
    tenant_id: api.tenant_id,
    name: findTenantName(api.tenant_id),
    alias: api.alias,
    created: formatDateLong(api.created_at),
    created_at: api.created_at,
  }))
);

onMounted(async () => {
  loadTable();
});

// Filter for search
const filter = ref({
  global: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  name: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  tenant_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  alias: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);
</script>
