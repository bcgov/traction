<script setup lang="ts">
import { inject } from "vue";
import Fieldset from "primevue/fieldset";
import ProgressSpinner from "primevue/progressspinner";
import axios from "axios";

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
        console.log(res);
        store.state.contacts.data = res.data.items;
      })
      .catch((err) => {
        store.state.contacts.data = null;
        console.error("error", err);
      });
  }
};
</script>

<template>
  <Fieldset
    :toggleable="true"
    :collapsed="!store.state.contacts.open"
    @toggle="toggled"
  >
    <template #legend>Contacts</template>

    <ProgressSpinner />
  </Fieldset>
</template>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
