<template>
  <h3 class="mt-0">Tenants</h3>

  <DataTable
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="tenants"
    :paginator="true"
    :rows="10"
    selection-mode="single"
    data-key="tenant_id"
    sortField="created_at"
    :sortOrder="-1"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <CheckInTenant />
        </div>
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
    <Column :expander="true" header-style="width: 3rem" />
    <Column :sortable="false" header="Actions">
      <template #body="{ data }">
        <Button
          title="Delete Contact"
          icon="pi pi-times-circle"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="deleteTenant($event, data)"
        />
      </template>
    </Column>
    <Column :sortable="true" field="name" header="Name" />
    <Column :sortable="true" field="wallet_id" header="Name" />
    <Column :sortable="true" field="public_did" header="Public DID" />
    <Column :sortable="true" field="issuer" header="Is Issuer" />
    <Column :sortable="true" field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData :id="data.tenant_id" :url="'/innkeeper/v1/tenants/'" />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import CheckInTenant from './CheckInTenant.vue';
import { formatDateLong } from '@/helpers';
import RowExpandData from '@/components/common/RowExpandData.vue';

const confirm = useConfirm();
const toast = useToast();

const innkeeperTenantsStore = useInnkeeperTenantsStore();

const { loading, tenants } = storeToRefs(useInnkeeperTenantsStore());

const loadTable = async () => {
  innkeeperTenantsStore.listTenants().catch((err: any) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});

const deleteTenant = (event: any, tenant: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this Tenant?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete(tenant);
    },
  });
};
const doDelete = (tenant: any) => {
  alert(`To be implemented ${JSON.stringify(tenant)}`);
};

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);
</script>
