<template>
  <h3 class="mt-0">My Received Presentations</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable v-model:selection="selectedPresentation" v-model:expandedRows="expandedRows" 
       :value="presentations" dataKey="verifier_presentation_id" :paginator="true" 
       :rows="10" striped-rows selection-mode="single"  @rowExpand="onRowExpand">
      <Column :expander="true" headerStyle="width: 3rem" />
      <Column :sortable="true" field="name" header="Name" />
      <Column field="contact.alias" header="Contact Name" />
      <Column field="state" header="State" />
      <Column field="status" header="Status" />
      <Column field="created_at" header="Created at" />
      <template #expansion="{data, index}">
          <PresentationDetails v-if='expandedRows[index]' :presentation="expandedRows[index]"/>
      </template>
    </DataTable>
  </div>
</template>


<script setup lang="ts">
import { onMounted, Ref, ref } from 'vue';
import Column from 'primevue/column';
import DataTable, { DataTableRowCollapseEvent } from 'primevue/datatable';
import ProgressSpinner from 'primevue/progressspinner';
import { useToast } from 'vue-toastification';

import { useVerifierStore } from '../../store';
import { storeToRefs } from 'pinia';


import PresentationDetails from './PresentationDetails.vue';
import { isTemplateNode } from '@vue/compiler-core';
const toast = useToast();

const verifierStore = useVerifierStore();
// use the loading state from the store to disable the button...
const { loading, presentations, selectedPresentation} = storeToRefs(useVerifierStore());

const loadTable = async () => {
  verifierStore.listPresentations().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

const expandedRows = ref([]) as Ref<any[]>; 

const onRowExpand = async (event: any) => {
  // fetch the item
  const row = await verifierStore.presentationDetailbyId(event.data.verifier_presentation_id);
  // if we expand only one...
  // expandedRows.value = [row];
  
  // if we are expanding multiple...
  // replace the item in rows with our full object
  const items = expandedRows.value.map((item: any) => {
    if (item.verifier_presentation_id == row.verifier_presentation_id) {
      return row;
    }
    return item;
  });
  expandedRows.value = items;
};

const onRowCollapse = (event: DataTableRowCollapseEvent) => {};

onMounted(async () => {
  loadTable();
});
</script>
