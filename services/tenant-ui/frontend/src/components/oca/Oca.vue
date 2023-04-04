<template>
  <h3 class="mt-0">
    {{ t('configuration.oca.oca') }}
  </h3>

  <DataTable
    v-model:expandedRows="expandedRows"
    v-model:filters="filter"
    :loading="loading"
    :value="ocas"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    selection-mode="single"
    data-key="oca_id"
    sort-field="created_at"
    :sort-order="-1"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <CreateOca />
        </div>
        <div class="flex justify-content-end">
          <span class="p-input-icon-left oca-search">
            <i class="pi pi-search" />
            <InputText
              v-model="filter.global.value"
              placeholder="Search OCA Items"
            />
          </span>
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
          title="Delete Credential Definition"
          icon="pi pi-trash"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="deleteOca($event, data.cred_def_id)"
        />
      </template>
    </Column>
    <Column
      :sortable="true"
      field="cred_def_id"
      header="ID"
      filter-field="cred_def_id"
    />

    <Column :sortable="true" field="url" header="OCA URL" filter-field="url" />

    <Column :sortable="true" field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <template #expansion="{ data }">
      <RowExpandData :id="data.oca_id" :url="API_PATH.OCA" />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue etc
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
// State
import { useGovernanceStore } from '../../store';
import { storeToRefs } from 'pinia';
// Custom components
import CreateOca from './createOca/CreateOca.vue';
import RowExpandData from '../common/RowExpandData.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';

const confirm = useConfirm();
const toast = useToast();
const { t } = useI18n();

const governanceStore = useGovernanceStore();
const { loading, ocas } = storeToRefs(useGovernanceStore());

// Loading the schema list and the stored cred defs
const loadTable = async () => {
  try {
    await governanceStore.listOcas();
  } catch (err) {
    console.error(err);
    toast.error(`Failure: ${err}`);
  }
};

onMounted(async () => {
  loadTable();
});

// Deleting a stored schema
const deleteOca = (event: any, id: string) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to remove this OCA association?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete(id);
    },
  });
};
const doDelete = (id: string) => {
  governanceStore
    .deleteOca(id)
    .then(() => {
      toast.success(`OCA record removed`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};

// necessary for expanding rows, we don't do anything with this
const expandedRows = ref([]);

// Filter for search
const filter = ref({
  global: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
});
</script>

<style scoped>
.row.buttons {
  float: right;
  margin: 3rem 1rem 0 0;
}

.p-datatable-header input {
  padding-left: 3rem;
  margin-right: 1rem;
}

.create-btn {
  margin-right: 1rem;
}

.oca-search {
  margin-left: 1.5rem;
}
</style>
