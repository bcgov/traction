<template>
  <h3 class="mt-0">Verifications</h3>

  <DataTable
    v-model:selection="selectedPresentation"
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="presentations"
    data-key="verifier_presentation_id"
    :paginator="true"
    :rows="TABLE_OPT.ROWS_DEFAULT"
    :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
    selection-mode="single"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <SuperYou
            :api-url="apiUrl"
            :template-json="templateJson"
            text="Create Presentation Request"
            icon="pi-key"
            @success="loadTable"
          />
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
    <Column :sortable="true" field="contact.alias" header="Contact Name" />
    <Column :sortable="true" field="status" header="Status">
      <template #body="{ data }">
        <StatusChip :status="data.status" />
      </template>
    </Column>
    <Column :sortable="true" field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
    <template #expansion="{ data }">
      <PresentationRowExpandData
        :row="data"
        :header="false"
        :show-information="true"
      />
    </template>
  </DataTable>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Button from 'primevue/button';
import { useToast } from 'vue-toastification';

import { useVerifierStore } from '../../store';
import { storeToRefs } from 'pinia';

import PresentationRowExpandData from './PresentationRowExpandData.vue';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import { formatDateLong } from '@/helpers';
import StatusChip from '../common/StatusChip.vue';
import SuperYou from '@/components/common/SuperYou.vue';
const toast = useToast();

const apiUrl = API_PATH.VERIFIER_PRESENTATION_ADHOC_REQUEST;

const templateJson = {
  contact_id: '67f68781-4dd9-49ad-9a5e-1e9a06e901f4',
  connection_id: '6530a727-8c05-4818-a1bb-687117afbd44',
  proof_request: {
    requested_attributes: [
      {
        name: 'string',
        names: ['string'],
        non_revoked: {},
        restrictions: [{}],
      },
    ],
    requested_predicates: [
      {
        name: 'string',
        p_type: '<',
        p_value: 0,
        non_revoked: {},
        restrictions: [{}],
      },
    ],
    non_revoked: {},
  },
  name: 'string',
  version: '1.0.0',
  external_reference_id: 'string',
  comment: 'string',
  tags: [],
};
// used by datatable expander behind the scenes
const expandedRows = ref([]);

const verifierStore = useVerifierStore();
// use the loading state from the store to disable the button...
const { loading, presentations, selectedPresentation } = storeToRefs(
  useVerifierStore()
);

const loadTable = async () => {
  verifierStore.listPresentations().catch((err) => {
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});
</script>

<style scoped>
.p-datatable-header input {
  padding-left: 3rem;
}
</style>
