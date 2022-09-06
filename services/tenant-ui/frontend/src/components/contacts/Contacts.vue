<template>
  <h3 class="mt-0">Connections</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable
      :value="contacts"
      :paginator="true"
      :rows="10"
      striped-rows
      selection-mode="single"
    >
      <template #header>
        <div class="flex justify-content-between">
          <CreateContact />
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
</template>

<script setup lang="ts">
// Vue
import { ref, onMounted } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import ProgressSpinner from 'primevue/progressspinner';

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

// do not use the loading from the store as that will cause a refresh of components...
// .. including the create invitation dialog (it needs to stay open)
const loading = ref(false);
const { contacts } = storeToRefs(useContactsStore());

const loadTable = async () => {
  loading.value = true;
  contactsStore
    .listContacts()
    .then(() => (loading.value = false))
    .catch((err) => {
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
