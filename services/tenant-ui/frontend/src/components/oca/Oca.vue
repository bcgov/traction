<template>
  <MainCardContent
    :title="$t('configuration.oca.oca')"
    :refresh-callback="loadTable"
  >
    <DataTable
      v-model:expandedRows="expandedRows"
      v-model:filters="filter"
      :loading="loading"
      :value="formattedOcas"
      :paginator="true"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      selection-mode="single"
      data-key="oca_id"
      sort-field="created_at"
      :sort-order="-1"
      filter-display="menu"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div class="flex justify-content-start">
            <CreateOca
              v-if="
                stringOrBooleanTruthy(config.frontend.showWritableComponents)
              "
            />
          </div>
          <div class="flex justify-content-end">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText
                v-model="filter.global.value"
                placeholder="Search OCA Items"
              />
            </span>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column :sortable="false" header="Actions">
        <template #body="{ data }">
          <Button
            v-if="stringOrBooleanTruthy(config.frontend.showWritableComponents)"
            title="Delete Credential Definition"
            icon="pi pi-trash"
            class="p-button-rounded p-button-icon-only p-button-text"
            @click="deleteOca($event, data.oca_id)"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="cred_def_id"
        header="Cred Def ID"
        filter-field="cred_def_id"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Cred Def ID"
            @input="filterCallback()"
          />
        </template>
      </Column>

      <Column :sortable="true" header="OCA Bundle">
        <template #body="{ data }">
          <span v-if="data.bundle">
            <i
              v-tooltip="'Bundle JSON stored in Traction, expand row to view'"
              class="pi pi-database"
            >
            </i>
            {{ $t('oca.json') }}
          </span>
          <span v-else-if="data.url">
            <i v-tooltip="'Bundle URL'" class="pi pi-link"> </i>
            {{ data.url }}
          </span>
        </template>
      </Column>

      <Column
        :sortable="true"
        field="created"
        header="Created at"
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
            placeholder="Search By Time"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <template #expansion="{ data }">
        <RowExpandData :id="data.oca_id" :url="API_PATH.OCAS" />
      </template>
    </DataTable>
  </MainCardContent>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref, Ref, computed } from 'vue';
// PrimeVue etc
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import { FilterMatchMode } from 'primevue/api';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useGovernanceStore } from '../../store';
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
const { config } = storeToRefs(useConfigStore());
// Custom components
import CreateOca from './createOca/CreateOca.vue';
import MainCardContent from '../layout/mainCard/MainCardContent.vue';
import RowExpandData from '../common/RowExpandData.vue';
import { TABLE_OPT, API_PATH } from '@/helpers/constants';
import { formatDateLong, stringOrBooleanTruthy } from '@/helpers';

const confirm = useConfirm();
const toast = useToast();

const governanceStore = useGovernanceStore();
const { loading, ocas } = storeToRefs(useGovernanceStore());

const formattedOcas: Ref<any[]> = computed(() =>
  ocas.value.map((oca) => ({
    oca_id: oca.oca_id,
    cred_def_id: oca.cred_def_id,
    bundle: oca.bundle,
    url: oca.url,
    created: formatDateLong(oca.created_at ?? ''),
    created_at: oca.created_at,
  }))
);
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
  },
  created: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
  cred_def_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  },
});
</script>

<style scoped>
.row.buttons {
  float: right;
  margin: 3rem 1rem 0 0;
}
</style>
