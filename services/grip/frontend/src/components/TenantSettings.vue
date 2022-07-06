<script setup lang="ts">
import { ref, inject } from "vue";
import axios from "axios";
import { useToast } from "vue-toastification";
import Fieldset from "primevue/fieldset";
import ProgressSpinner from "primevue/progressspinner";

const store: any = inject("store");
const toast = useToast();

// For state
let setting_open_toggle: boolean = false;

// Vite passes the api url to here
const api = import.meta.env.VITE_TRACTION_ENDPOINT;

const toggled = (e: any) => {
  setting_open_toggle = !e.value;
  console.log("toggled", setting_open_toggle); //why is this in the store?

  if (setting_open_toggle && !store.state.settings.self) {
    axios
      .get(`${api}/v1/tenant/admin/self`, {
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${store.state.token}`,
        },
      })
      .then((res) => {
        store.state.settings.self = res.data.item;
        console.log(store.state.settings.self);
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
    :collapsed="!setting_open_toggle"
    @toggle="toggled"
  >
    <template #legend>Settings</template>
    <ProgressSpinner v-if="!store.state.settings.self" />
    <div v-else>
      {{ store.state.admin_settings }}
    </div>
  </Fieldset>
</template>


<script lang="ts">
export default {
  name: "TenantSettings",
};
</script>

<style></style>
