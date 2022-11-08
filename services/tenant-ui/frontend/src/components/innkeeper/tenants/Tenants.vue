<template>
  <h3 class="mt-0">{{ t('tenants.tenants') }}</h3>

  <DataTable
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="tenants"
    :paginator="true"
    :rows="10"
    selection-mode="single"
    data-key="tenant_id"
    sort-field="created_at"
    :sort-order="-1"
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
    <Column :sortable="true" field="name" header="Name" />
    <Column :sortable="true" field="wallet_id" header="Wallet ID" />
    <Column :sortable="true" field="public_did" header="Public DID" />
    <Column :sortable="true" field="issuer" header="Issuer">
      <template #body="{ data }">
        <i v-if="data.issuer" class="pi pi-check-circle" />
      </template>
    </Column>
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
import { useToast } from 'vue-toastification';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import CheckInTenant from './CheckInTenant.vue';
import { formatDateLong } from '@/helpers';
import RowExpandData from '@/components/common/RowExpandData.vue';
import { useI18n } from 'vue-i18n';

const toast = useToast();
const { t } = useI18n();

const innkeeperTenantsStore = useInnkeeperTenantsStore();

const { loading, tenants } = storeToRefs(useInnkeeperTenantsStore());
console.log('tenants', tenants);

const loadTable = async () => {
  innkeeperTenantsStore.listTenants().catch((err: string) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);
</script>
