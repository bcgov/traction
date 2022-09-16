<template>
  <h3 class="mt-0">Verifications</h3>

  <DataTable
    v-model:selection="selectedPresentation"
    v-model:expandedRows="expandedRows"
    :loading="loading"
    :value="presentations"
    data-key="verifier_presentation_id"
    :paginator="true"
    :rows="10"
    selection-mode="single"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start"></div>
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
    <Column field="contact.alias" header="Contact Name" />
    <Column field="status" header="Status" />
    <Column field="created_at" header="Created at">
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
import { formatDateLong } from '@/helpers';
const toast = useToast();

// used by datatable expander behind the scenes
const expandedRows = ref([]);

const verifierStore = useVerifierStore();
// use the loading state from the store to disable the button...
const { loading, presentations, selectedPresentation } = storeToRefs(
  useVerifierStore()
);

const loadTable = async () => {
  verifierStore.listPresentations().catch((err) => {
    console.error(err);
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
