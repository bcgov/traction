<script setup lang="ts">
import { inject } from "vue";
import Fieldset from "primevue/fieldset";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import ProgressSpinner from "primevue/progressspinner";
import axios from "axios";
import Button from "primevue/button";

const store: any = inject("store");

// Vite passes the api url to here
const api = import.meta.env.VITE_TRACTION_ENDPOINT;

const toggled = (e: any) => {
  store.state.contacts.open = !e.value;
  console.log("toggled", store.state.contacts.open);

  if (store.state.contacts.open && !store.state.contacts.data) {
    axios
      .get(`${api}/tenant/v1/contacts`, {
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
  console.log("createContact");
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
        :rows="5"
        striped-rows
        v-model:selection="store.state.contacts.selection"
        selection-mode="single"
      >
        <Column :sortable="true" field="alias" header="Name" />
        <Column field="roll" header="Roll" />
        <Column field="state" header="State" />
        <Column field="status" header="Status" />
        <Column field="created_at" header="Created at" />
        <Column field="contact_id" header="ID" />
      </DataTable>
    </div>
    <Button
      class="create-contact"
      icon="pi pi-plus"
      label="Create Contact"
      @click="createContact"
    ></Button>
  </Fieldset>
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
