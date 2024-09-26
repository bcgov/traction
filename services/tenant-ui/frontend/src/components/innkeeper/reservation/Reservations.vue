<template>
  <MainCardContent
    :title="$t('reservations.reservations')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:expanded-rows="expandedRows"
      v-model:filters="filter"
      :loading="loading"
      :value="formattedReservations"
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
              placeholder="Search Reservations"
            />
          </IconField>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column :sortable="false" header="Actions">
        <template #body="{ data }">
          <ApproveReservation
            :id="data.reservation_id"
            :email="data.contact_email"
            :name="data.tenant_name"
            @success="showApproveModal"
          />
          <DenyReservation
            :id="data.reservation_id"
            :email="data.contact_email"
            :name="data.tenant_name"
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

  <!-- Post-approve dialog -->
  <Dialog
    v-model:visible="displayModal"
    :header="$t('reservations.approved.title')"
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
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputIcon from 'primevue/inputicon';
import IconField from 'primevue/iconfield';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'vue-toastification';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import ApproveReservation from './ApproveReservation.vue';
import DenyReservation from './DenyReservation.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import { TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const toast = useToast();

const innkeeperTenantsStore = useInnkeeperTenantsStore();
const { loading, currentReservations } = storeToRefs(
  useInnkeeperTenantsStore()
);

const formattedReservations = computed(() =>
  currentReservations.value.map((msg) => ({
    state: msg.state,
    reservation_id: msg.reservation_id,
    contact_email: msg.contact_email,
    tenant_name: msg.tenant_name,
    context_data: msg.context_data,
    created_at: msg.created_at,
    created: formatDateLong(msg.created_at),
  }))
);
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

// Handling approvals
const displayModal = ref(false);
const approvedPassword = ref('');
const approvedEmail = ref('');
const showApproveModal = (password: string, email: string) => {
  approvedPassword.value = password;
  approvedEmail.value = email;
  displayModal.value = true;
};

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
