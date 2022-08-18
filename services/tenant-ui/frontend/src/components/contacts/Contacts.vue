<template>
  <h3 class="mt-0">Connections</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable v-model:selection="selection" :value="contacts" :paginator="true" :rows="10" striped-rows selection-mode="single">
      <Column :sortable="true" field="alias" header="Name" />
      <Column field="role" header="Role" />
      <Column field="state" header="State" />
      <Column field="status" header="Status" />
      <Column field="created_at" header="Created at" />
      <Column field="contact_id" header="ID" />
    </DataTable>
  </div>
  <Button v-if="contacts" class="create-contact" icon="pi pi-plus" label="Create Contact" @click="createContact"></Button>

  <Dialog v-model:visible="displayAddContact" header="Create a new contact" :modal="true">
    <CreateContact @created="contactCreated" />
  </Dialog>
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

// Other imports
import { useToast } from 'vue-toastification';
import { useContactsStore } from '../../store/contactsStore';
import { storeToRefs } from 'pinia';

// Other components
import CreateContact from './CreateContact.vue';

const contactsStore = useContactsStore();
const toast = useToast();

// use the loading state from the store to disable the button...
const { loading, contacts, selection } = storeToRefs(useContactsStore());

const loadContacts = async () => {
  await contactsStore.load().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

onMounted(async () => {
  await loadContacts();
});
// -----------------------------------------------/Loading contacts

// ----------------------------------------------------------------
// Adding Contacts
// ----------------------------------------------------------------
const displayAddContact = ref(false);

const createContact = () => {
  displayAddContact.value = !displayAddContact.value;
};

const contactCreated = async () => {
  // Emited from the contact creation component when a successful invite is made
  console.log('contact created emit - do we want to "manually" load contacts or have the store automatically do it?');
  await loadContacts();
};
// -----------------------------------------------/Adding contacts
</script>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}

.create-contact {
  float: right;
  margin-top: 10px;
}
</style>
