<template>
  <h3 class="mt-0">{{ t('reservations.reservationHistory') }}</h3>

  <DataTable
    v-model:filters="filter"
    :loading="loading"
    :value="reservationHistory"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    selection-mode="single"
    data-key="reservation_id"
    sort-field="created_at"
    :sort-order="-1"
  >
    <template #header>
      <div class="flex justify-content-end">
        <span class="p-input-icon-left mr-3">
          <i class="pi pi-search ml-0" />
          <InputText
            v-model="filter.global.value"
            placeholder="Search History"
          />
        </span>
        <Button
          icon="pi pi-refresh"
          class="p-button-rounded p-button-outlined"
          title="Refresh Table"
          @click="loadTable"
        />
      </div>
    </template>
    <template #empty> No records found. </template>
    <template #loading> Loading data. Please wait... </template>
    <Column :sortable="true" field="state" header="State">
      <template #body="{ data }">
        <StatusChip :status="data.state" />
      </template>
    </Column>
    <Column :sortable="true" field="reservation_id" header="id" />
    <Column :sortable="true" field="contact_email" header="Contact Email" />
    <Column :sortable="true" field="contact_name" header="Contact Name" />
    <Column :sortable="true" field="contact_phone" header="Contact Phone" />
    <Column :sortable="true" field="tenant_name" header="Tenant Name" />
    <Column :sortable="true" field="tenant_reason" header="Tenant Reason" />
    <Column :sortable="true" field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
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
import { useI18n } from 'vue-i18n';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import StatusChip from '@/components/common/StatusChip.vue';
import { TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const toast = useToast();
const { t } = useI18n();

const innkeeperTenantsStore = useInnkeeperTenantsStore();

const { loading, reservationHistory } = storeToRefs(useInnkeeperTenantsStore());

// Loading table contents
const loadTable = async () => {
  innkeeperTenantsStore.listReservations().catch((err: string) => {
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
</script>
