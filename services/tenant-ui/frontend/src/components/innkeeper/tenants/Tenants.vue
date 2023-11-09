<template>
  <MainCardContent :title="$t('tenants.tenants')" :refresh-callback="loadTable">
    <DataTable
      v-model:expandedRows="expandedRows"
      v-model:filters="filter"
      :loading="loading"
      :value="formattedTenants"
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
          <div class="flex justify-content-start"></div>
          <div class="flex justify-content-end">
            <div class="container">
              <ToggleButton
                v-model="showDeleted"
                :on-label="$t('common.hideDeleted')"
                :off-label="$t('common.showDeleted')"
                class="mr-2 container-item"
                style="width: 10rem"
                @change="loadTable"
              />
              <span class="p-input-icon-left container-item">
                <i class="pi pi-search ml-0" />
                <InputText
                  v-model="filter.global.value"
                  :placeholder="$t('tenants.search')"
                />
              </span>
            </div>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column :sortable="false" :header="$t('common.actions')">
        <template #body="{ data }">
          <div v-if="data.state == 'active'" class="container">
            <EditConfig :tenant="data" />
            <DeleteTenant :tenant="data" />
          </div>
          <div v-else class="container-item deleted-btn">
            {{ $t('common.deleted') }}
          </div>
        </template>
      </Column>
      <Column
        :sortable="true"
        field="tenant_name"
        :header="$t('common.name')"
        filter-field="tenant_name"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="$t('common.searchByName')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="created"
        :header="$t('common.createdAt')"
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
            :placeholder="$t('common.searchByCreated')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="deleted"
        :header="$t('common.deletedAt')"
        filter-field="deleted"
        :show-filter-match-modes="false"
        :hidden="!showDeleted"
      >
        <template #body="{ data }">
          {{ data.deleted }}
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="$t('common.searchByDeleted')"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <template #expansion="{ data }">
        <RowExpandData :id="data.tenant_id" :url="API_PATH.INNKEEPER_TENANTS" />
      </template>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import ToggleButton from 'primevue/togglebutton';
import { computed, onMounted, ref } from 'vue';
import { useToast } from 'vue-toastification';

import RowExpandData from '@/components/common/RowExpandData.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import { formatDateLong } from '@/helpers';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import { useInnkeeperTenantsStore } from '@/store';
import DeleteTenant from './deleteTenant/DeleteTenant.vue';
import EditConfig from './editConfig/editConfig.vue';

const toast = useToast();

const innkeeperTenantsStore = useInnkeeperTenantsStore();
const showDeleted = ref(false);

// Populating the Table
const { loading, tenants } = storeToRefs(useInnkeeperTenantsStore());
const loadTable = () => {
  innkeeperTenantsStore
    .listTenants(showDeleted.value ? 'all' : 'active')
    .catch((err: string) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};

// Formatting the Tenant table row
const formattedTenants = computed(() =>
  tenants.value.map((ten: any) => ({
    tenant_id: ten.tenant_id,
    tenant_name: ten.tenant_name,
    connect_to_endorser: ten.connect_to_endorser,
    created_public_did: ten.created_public_did,
    created: formatDateLong(ten.created_at),
    created_at: ten.created_at,
    enable_ledger_switch: ten.enable_ledger_switch,
    state: ten.state,
    deleted: formatDateLong(ten.deleted_at),
    deleted_at: ten.deleted_at,
  }))
);

onMounted(() => {
  loadTable();
});

// Filter for search
const filter = ref({
  global: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  tenant_name: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  deleted: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);
</script>
<style scoped>
.container {
  display: flex;
}
.container-item {
  height: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
}
.deleted-btn {
  height: 2.625rem;
  background-color: #ef4444;
  border: 1px solid #ef4444;
  color: white;
  border-radius: 10px;
  width: 50%;
  font-weight: 600;
}
</style>
