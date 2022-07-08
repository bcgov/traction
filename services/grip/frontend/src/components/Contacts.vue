<script setup lang="ts">
import { inject, ref } from "vue";
import Fieldset from "primevue/fieldset";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import ProgressSpinner from "primevue/progressspinner";
import axios from "axios";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import CreateContact from "./CreateContact.vue";

const store: any = inject("store");

// Vite passes the api url to here
const api = import.meta.env.VITE_TRACTION_ENDPOINT;

let displayAddContact = ref(false);

const toggled = (e: any) => {
  store.state.contacts.open = !e.value;
  console.log("toggled", store.state.contacts.open);

  if (store.state.contacts.open && !store.state.contacts.data) {
    axios
      .get(`${api}/tenant/v1/contacts?page_size=1000`, {
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${store.state.token}`,
        },
      })
      .then((res) => {
        store.state.contacts.data = res.data.items;
        console.log(store.state.contacts.data);
      })
      .catch((err) => {
        store.state.contacts.data = null;
        console.error("error", err);
      });
  }
};

const createContact = () => {
  displayAddContact.value = !displayAddContact.value;
};
</script>

<template>
  <Fieldset
    :toggleable="true"
    :collapsed="!store.state.contacts.open"
    @toggle="toggled"
  >
    <template #legend>Contacts</template>

    <!--
      If there is no data, show a spinner.
      Otherwise show the data.
    -->
    <ProgressSpinner v-if="!store.state.contacts.data" />
    <div v-else>
      <DataTable
        :value="store.state.contacts.data"
        :paginator="true"
        :rows="10"
        striped-rows
        v-model:selection="store.state.contacts.selection"
        selection-mode="single"
      >
        <Column :sortable="true" field="alias" header="Name" />
        <Column field="role" header="Role" />
        <Column field="state" header="State" />
        <Column field="status" header="Status" />
        <Column field="created_at" header="Created at" />
        <Column field="contact_id" header="ID" />
      </DataTable>
    </div>
    <Button
      v-if="store.state.contacts.data"
      class="create-contact"
      icon="pi pi-plus"
      label="Create Contact"
      @click="createContact"
    ></Button>
  </Fieldset>

  <Dialog
    header="Create a new contact"
    v-model:visible="displayAddContact"
    :modal="true"
  >
    <CreateContact />
  </Dialog>
</template>

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
