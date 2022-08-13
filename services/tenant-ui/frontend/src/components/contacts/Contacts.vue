<template>
  <h3 class="mt-0">Connections</h3>

  <ProgressSpinner v-if="loading" />
  <div v-else>
    <DataTable :value="store.state.contacts.data" :paginator="true" :rows="10" striped-rows v-model:selection="store.state.contacts.selection" selection-mode="single">
      <Column :sortable="true" field="alias" header="Name" />
      <Column field="role" header="Role" />
      <Column field="state" header="State" />
      <Column field="status" header="Status" />
      <Column field="created_at" header="Created at" />
      <Column field="contact_id" header="ID" />
    </DataTable>
  </div>
  <Button v-if="store.state.contacts.data" class="create-contact" icon="pi pi-plus" label="Create Contact" @click="createContact"></Button>

  <Dialog header="Create a new contact" v-model:visible="displayAddContact" :modal="true">
    <CreateContact @created="contactCreated" />
  </Dialog>
</template>

<script setup lang="ts">
// Vue
import { inject, ref, onMounted } from 'vue';

// PrimeVue
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import ProgressSpinner from 'primevue/progressspinner';

// Other imports
import axios from 'axios';
import { useToast } from 'vue-toastification';

// Other components
import CreateContact from './CreateContact.vue';

// Store
const store: any = inject('store');

// ----------------------------------------------------------------
// Loading contacts
// ----------------------------------------------------------------
let loading = ref(true);

const loadContacts = () => {
  console.log('yo me');
  loading.value = true;

  const toast = useToast();
  toast('testing');

  // toast.add({
  //   severity: 'info',
  //   summary: 'Loading contacts',
  //   detail: 'Please wait...',
  // });
  axios
    .get('/api/traction/tenant/v1/contacts', {
      headers: {
        accept: 'application/json',
        Authorization: `Bearer ${store.state.token}`,
      },
    })
    .then((res) => {
      store.state.contacts.data = res.data.items;
      console.log(store.state.contacts.data);
      loading.value = false;
    })
    .catch((err) => {
      store.state.contacts.data = null;
      console.error('error', err);
    });
};

onMounted(() => {
  loadContacts();
});
// -----------------------------------------------/Loading contacts

// ----------------------------------------------------------------
// Adding Contacts
// ----------------------------------------------------------------
let displayAddContact = ref(false);

const createContact = () => {
  displayAddContact.value = !displayAddContact.value;
};

const contactCreated = () => {
  // Emited from the contact creation component when a successful invite is made
  loadContacts();
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
