<template>
  <MainCardContent
    :title="$t('reservations.reservationHistory')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:expandedRows="expandedRows"
      v-model:filters="filter"
      :loading="loading"
      :value="formattedReservationHistory"
      :paginator="true"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      selection-mode="single"
      data-key="reservation_id"
      sort-field="created_at"
      :sort-order="-1"
      filter-display="menu"
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
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column
        :sortable="true"
        field="state"
        filter-field="state"
        header="State"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          <StatusChip :status="data.state" />
          <RefreshReservation
            v-if="data.state === 'approved'"
            :id="data.id"
            :email="data.contact_email"
          />
          />
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
        field="reservation_id"
        filter-field="reservation_id"
        header="id"
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
        field="contact_email"
        filter-field="contact_email"
        header="Contact Email"
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
        field="tenant_name"
        filter-field="tenant_name"
        header="Tenant Name"
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
        filter-field="created"
        header="Created at"
        :show-filter-match-modes="false"
      >
        <template #body="{ data }">
          {{ formatDateLong(data.created_at) }}
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
        <Accordion>
          <AccordionTab header="View Raw Content">
            <vue-json-pretty :data="data" />
          </AccordionTab>
        </Accordion>
      </template>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, computed } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'vue-toastification';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import StatusChip from '@/components/common/StatusChip.vue';
import RefreshReservation from './RefreshReservation.vue';
import { TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const toast = useToast();

const innkeeperTenantsStore = useInnkeeperTenantsStore();

const { loading, reservationHistory } = storeToRefs(useInnkeeperTenantsStore());

// Loading table contents
const loadTable = async () => {
  innkeeperTenantsStore.listReservations().catch((err: string) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};
const formattedReservationHistory = computed(() =>
  reservationHistory.value.map((msg) => ({
    state: msg.state,
    reservation_id: msg.reservation_id,
    contact_email: msg.contact_email,
    tenant_name: msg.tenant_name,
    context_data: msg.context_data,
    created_at: msg.created_at,
    created: formatDateLong(msg.created_at),
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
  } as DataTableFilterMetaData,
  state: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  reservation_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  contact_email: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  tenant_name: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
});
// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);
</script>
