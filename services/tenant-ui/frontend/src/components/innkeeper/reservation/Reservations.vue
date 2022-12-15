<template>
  <h3 class="mt-0">{{ t('reservations.reservations') }}</h3>

  <DataTable
    :loading="loading"
    :value="reservations"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    selection-mode="single"
    data-key="reservation_id"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-end">
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-button-outlined"
            title="Refresh Table"
            @click="loadTable"
          />
        </div>
      </div>
    </template>
    <template #empty> No records found. </template>
    <template #loading> Loading data. Please wait... </template>
    <Column :sortable="false" header="Actions">
      <template #body="{ data }">
        <Button
          title="Approve Reservation"
          icon="pi pi-check"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="approve($event, data)"
        />
        <Button
          title="Deny Reservation"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="deny($event, data)"
        />
      </template>
    </Column>
    <Column :sortable="true" field="reservation_id" header="ID" />
    <Column :sortable="true" field="state" header="State" />
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
import DataTable from 'primevue/datatable';
import { useToast } from 'vue-toastification';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import { TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';
import { useI18n } from 'vue-i18n';

const toast = useToast();
const { t } = useI18n();

const innkeeperTenantsStore = useInnkeeperTenantsStore();

const { loading, reservations } = storeToRefs(useInnkeeperTenantsStore());

// Approve/deny reservation
const approve = (event: any, row: any) => {
  alert('approve');
};
const deny = (event: any, row: any) => {
  alert('deny');
};

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
</script>
