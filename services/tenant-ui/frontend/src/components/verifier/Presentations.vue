<template>
  <h3 class="mt-0">My Received Presentations</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable
      v-model:selection="selectedPresentation"
      v-model:expandedRows="expandedRows"
      :value="presentations"
      data-key="verifier_presentation_id"
      :paginator="true"
      :rows="10"
      striped-rows
      selection-mode="single"
      @row-expand="onRowExpand"
    >
      <template #header>
        <div class="flex justify-content-between">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText placeholder="Presentation Search" disabled />
          </span>
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-button-outlined"
            title="Refresh Table"
            @click="loadTable"
          ></Button>
        </div>
      </template>
      <Column :expander="true" header-style="width: 3rem" />
      <Column :sortable="true" field="name" header="Name" />
      <Column field="contact.alias" header="Contact Name" />
      <Column field="state" header="State" />
      <Column field="status" header="Status" />
      <Column field="created_at" header="Created at">
        <template #body="{ data }">
          {{ formatDateLong(data.created_at) }}
        </template>
      </Column>
      <template #expansion="{ data }">
        <PresentationDetails
          :presentation="presentationDetailDict[data.verifier_presentation_id]"
          :header="false"
        />
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';

import { useVerifierStore } from '../../store';
import { storeToRefs } from 'pinia';

import PresentationDetails from './PresentationDetails.vue';
import { formatDateLong } from '@/helpers';
const toast = useToast();

// used by datatable expander behind the scenes
const expandedRows = ref([]);

const verifierStore = useVerifierStore();
// use the loading state from the store to disable the button...
const { loading, presentations, selectedPresentation, presentationDetailDict } =
  storeToRefs(useVerifierStore());

const loadTable = async () => {
  verifierStore.listPresentations().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

const onRowExpand = (event: any) => {
  verifierStore.getPresentationDetails(event.data.verifier_presentation_id);
};

const onRowCollapse = (event: any) => {};

onMounted(async () => {
  loadTable();
});
</script>

<style scoped>
.p-datatable-header input {
  padding-left: 3rem;
}
</style>