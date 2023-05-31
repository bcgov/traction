<template>
  <h3 class="mt-0">{{ $t('tenants.tenants') }}</h3>

  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="tenants"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    selection-mode="single"
    data-key="tenant_id"
    sort-field="created_at"
    :sort-order="-1"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start"></div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left mr-3">
            <i class="pi pi-search ml-0" />
            <InputText
              v-model="filter.global.value"
              placeholder="Search Tenants"
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
    <template #empty>{{ $t('common.noRecordsFound') }}</template>
    <template #loading>{{ $t('common.loading') }}</template>
    <Column :expander="true" header-style="width: 3rem" />
    <Column :sortable="false" :header="$t('common.actions')">
      <template #body="{ data }">
        <EditConfig :tenant="data" />
      </template>
    </Column>
    <Column :sortable="true" field="tenant_name" header="Name" />
    <Column :sortable="true" field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData :id="data.tenant_id" :url="API_PATH.INNKEEPER_TENANTS" />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'vue-toastification';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';
import RowExpandData from '@/components/common/RowExpandData.vue';
import EditConfig from './editConfig/editConfig.vue';

const toast = useToast();

const innkeeperTenantsStore = useInnkeeperTenantsStore();

// Populating the Table
const { loading, tenants } = storeToRefs(useInnkeeperTenantsStore());
const loadTable = async () => {
  innkeeperTenantsStore.listTenants().catch((err: string) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});

// Filter for search
const filter = ref({
  global: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
});

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);
</script>
