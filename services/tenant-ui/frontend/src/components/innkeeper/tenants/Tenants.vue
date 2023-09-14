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
            <span class="p-input-icon-left">
              <i class="pi pi-search ml-0" />
              <InputText
                v-model="filter.global.value"
                placeholder="Search Tenants"
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
          <EditConfig :tenant="data" />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="tenant_name"
        header="Name"
        filter-field="tenant_name"
        :show-filter-match-modes="false"
      >
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
            placeholder="Search By Contact"
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
import { formatDateLong } from '@/helpers';
import EditConfig from './editConfig/editConfig.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';

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

// Formatting the Tenant table row
const formattedTenants = computed(() =>
  tenants.value.map((ten: any) => ({
    tenant_id: ten.tenant_id,
    tenant_name: ten.tenant_name,
    connect_to_endorser: ten.connect_to_endorser,
    created_public_did: ten.created_public_did,
    created: formatDateLong(ten.created_at),
    created_at: ten.created_at,
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
  tenant_name: {
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
