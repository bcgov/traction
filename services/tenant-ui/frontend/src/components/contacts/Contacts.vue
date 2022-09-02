<template>
  <h3 class="mt-0">Connections</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable
      v-model:selection="selectedContact"
      :value="contacts"
      :paginator="true"
      :rows="10"
      striped-rows
      selection-mode="single"
    >
      <template #header>
        <div class="flex justify-content-between">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText placeholder="Connection Search" disabled />
          </span>
          <Button
            icon="pi pi-refresh"
            class="p-button-rounded p-button-outlined"
            title="Refresh Table"
            @click="loadTable"
          ></Button>
        </div>
      </template>
      <Column :sortable="true" field="alias" header="Name" />
      <Column field="role" header="Role" />
      <Column field="state" header="State" />
      <Column field="status" header="Status" />
      <Column field="created_at" header="Created at">
        <template #body="{ data }">
          {{ formatDateLong(data.created_at) }}
        </template>
      </Column>
      <Column field="contact_id" header="ID" />
    </DataTable>
  </div>
  <div class="flex justify-content-end flex-wrap m-3 gap-3">
    <CreateContact />
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref, onMounted } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import ProgressSpinner from 'primevue/progressspinner';
import InputText from 'primevue/inputtext';
// State
import { useContactsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other imports
import { useToast } from 'vue-toastification';
// Other components
import CreateContact from './createContact/CreateContact.vue';
import { formatDateLong } from '@/helpers';

const toast = useToast();

const contactsStore = useContactsStore();
// use the loading state from the store to disable the button...
const { loading, contacts, selectedContact } = storeToRefs(useContactsStore());

const loadTable = async () => {
  contactsStore.listContacts().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  loadTable();
});
</script>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}

.p-datatable-header input {
  padding-left: 3rem;
}
</style>
