<template>
  <MainCardContent :title="$t('tenants.tenants')" :refresh-callback="loadTable">
    <DataTable
      v-model:expanded-rows="expandedRows"
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
                v-model="showSuspended"
                :on-label="$t('common.hideSuspended')"
                :off-label="$t('common.showSuspended')"
                class="mr-2 container-item"
                style="width: 10rem"
                @change="loadTable"
              />
              <IconField class="container-item" icon-position="left">
                <InputIcon><i class="pi pi-search" /></InputIcon>
                <InputText
                  v-model="filter.global.value"
                  :placeholder="$t('tenants.search')"
                />
              </IconField>
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
          <div v-else class="container">
            <span class="container-item deleted-btn">
              {{ $t('common.suspended') }}
            </span>
            <RestoreTenant :id="data.tenant_id" :name="data.tenant_name" />
            <DeleteTenant :tenant="data" unsuspendable />
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
        field="curr_ledger_id"
        header="Write Ledger"
        filter-field="curr_ledger_id"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Write Ledger"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="contact_email"
        header="Contact Email"
        filter-field="contact_email"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <div v-if="data.contact_email" class="flex align-items-center gap-2">
            <a :href="'mailto:' + data.contact_email">
              {{ data.contact_email }}
            </a>
          </div>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Contact Email"
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
        :header="$t('common.suspendedAt')"
        filter-field="deleted"
        :show-filter-match-modes="false"
        :hidden="!showSuspended"
      >
        <template #body="{ data }">
          {{ data.deleted_at }}
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            :placeholder="$t('common.searchBySuspended')"
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
import { FilterMatchMode } from 'primevue/api';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import InputIcon from 'primevue/inputicon';
import IconField from 'primevue/iconfield';
import ToggleButton from 'primevue/togglebutton';
import { computed, onMounted, ref } from 'vue';
import { useToast } from 'vue-toastification';

// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatTenants } from '@/helpers/tableFormatters';
import EditConfig from './editConfig/editConfig.vue';
import DeleteTenant from './deleteTenant/DeleteTenant.vue';
import RestoreTenant from './deleteTenant/RestoreTenant.vue';
import RowExpandData from '@/components/common/RowExpandData.vue';
const toast = useToast();

const innkeeperTenantsStore = useInnkeeperTenantsStore();
const showSuspended = ref(false);

// Populating the Table
const { loading, tenants } = storeToRefs(useInnkeeperTenantsStore());
const loadTable = () => {
  innkeeperTenantsStore
    .listTenants(showSuspended.value ? 'all' : 'active')
    .catch((err: string) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};

// Formatting the Tenant table row
const formattedTenants = computed(() => formatTenants(tenants));

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
  curr_ledger_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  contact_email: {
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
