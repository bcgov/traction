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
    sort-field="created_at"
    :sort-order="-1"
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
        <ApproveReservation
          :id="data.reservation_id"
          :email="data.contact_email"
          @success="showApproveModal"
        />
        <DenyReservation
          :id="data.reservation_id"
          :email="data.contact_email"
        />
      </template>
    </Column>
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

  <!-- Post-approve dialog -->
  <Dialog
    v-model:visible="displayModal"
    :header="t('reservations.approved.title')"
    :modal="true"
  >
    <p>
      {{ t('reservations.approved.text', { email: approvedEmail }) }}
    </p>
    <p>
      The password is shown below one-time if you need to communicate it via
      other means <br />
      <strong>{{ approvedPassword }}</strong>
    </p>
  </Dialog>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import ApproveReservation from './ApproveReservation.vue';
import DenyReservation from './DenyReservation.vue';
import StatusChip from '@/components/common/StatusChip.vue';
import { TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const toast = useToast();
const { t } = useI18n();

const innkeeperTenantsStore = useInnkeeperTenantsStore();

const { loading, reservations } = storeToRefs(useInnkeeperTenantsStore());

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
</script>
