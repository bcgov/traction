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
      <Column :expander="true" header-style="width: 3rem" />
      <Column :sortable="true" field="name" header="Name" />
      <Column field="contact.alias" header="Contact Name" />
      <Column field="state" header="State" />
      <Column field="status" header="Status" />
      <Column field="created_at" header="Created at" />
      <template #expansion="{ data }">
        <PresentationDetails
          :presentation="presentationDetailDict[data.verifier_presentation_id]"
        />
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import ProgressSpinner from 'primevue/progressspinner';
import { useToast } from 'vue-toastification';

import { useVerifierStore } from '../../store';
import { storeToRefs } from 'pinia';

import PresentationDetails from './PresentationDetails.vue';
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
