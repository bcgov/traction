<template>
  <h3 class="mt-0">Contacts</h3>

  <DataTable
    v-model:selection="selectedContact"
    :loading="loading"
    :value="contacts"
    :paginator="true"
    :rows="10"
    striped-rows
    selection-mode="single"
  >
    <template #header>
      <div class="flex justify-content-between">
        <div class="flex justify-content-start">
          <CreateContact />
          <AcceptInvitation class="ml-4" />
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
    <Column :sortable="true" field="alias" header="Name" />
    <Column field="role" header="Role" />
    <Column field="status" header="Status" />
    <Column field="created_at" header="Created at">
      <template #body="{ data }">
        {{ formatDateLong(data.created_at) }}
      </template>
    </Column>
  </DataTable>
</template>

<script setup lang="ts">
// Vue
import { onMounted } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';

// State
import { useContactsStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other imports
import { useToast } from 'vue-toastification';
// Other components
import AcceptInvitation from './acceptInvitation/AcceptInvitation.vue';
import CreateContact from './createContact/CreateContact.vue';
import { formatDateLong } from '@/helpers';

const toast = useToast();

const contactsStore = useContactsStore();

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
// -----------------------------------------------/Loading contacts
</script>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}

.create-contact {
  float: right;
  margin: 3rem 1rem 0 0;
}
.p-datatable-header input {
  padding-left: 3rem;
}
</style>
