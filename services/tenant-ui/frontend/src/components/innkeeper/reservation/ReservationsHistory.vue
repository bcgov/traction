<template>
  <MainCardContent
    :title="$t('reservations.reservationHistory')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:expanded-rows="expandedRows"
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
          <IconField icon-position="left">
            <InputIcon><i class="pi pi-search" /></InputIcon>
            <InputText
              v-model="filter.global.value"
              placeholder="Search History"
            />
          </IconField>
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
          <div class="state-container">
            <StatusChip :status="data.state" />
            <RefreshPassword
              v-if="data.state === 'approved'"
              :id="data.reservation_id"
              :email="data.contact_email"
              @success="showModal"
            />
          </div>
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

  <Dialog
    v-model:visible="displayModal"
    :header="$t('reservations.refreshed.title')"
    :modal="true"
  >
    <p>
      {{ $t('reservations.approved.text', { email: approvedEmail }) }}
    </p>
    <p>
      {{ $t('reservations.otp') }} <br />
      <strong>{{ approvedPassword }}</strong>
    </p>
  </Dialog>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, computed } from 'vue';

// PrimeVue
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputIcon from 'primevue/inputicon';
import IconField from 'primevue/iconfield';
import { FilterMatchMode } from 'primevue/api';

// external
import VueJsonPretty from 'vue-json-pretty';
import { useToast } from 'vue-toastification';

// store
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';

// Importing internal and helpers
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import RefreshPassword from './RefreshPassword.vue';
import StatusChip from '@/components/common/StatusChip.vue';
import { formatDateLong } from '@/helpers';
import { TABLE_OPT } from '@/helpers/constants';

const toast = useToast();

// modal
const displayModal = ref(false);
const approvedPassword = ref('');
const approvedEmail = ref('');

const innkeeperTenantsStore = useInnkeeperTenantsStore();
const { loading, reservationHistory } = storeToRefs(useInnkeeperTenantsStore());

const showModal = (password: string, email: string) => {
  approvedPassword.value = password;
  approvedEmail.value = email;
  displayModal.value = true;
};

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
<style scoped>
.state-container {
  display: flex;
}
</style>
