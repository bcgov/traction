<script setup lang="ts">
import { ref, inject } from "vue";
import axios from "axios";
import { useToast } from "vue-toastification";
import Fieldset from "primevue/fieldset";
import Button from "primevue/button";
import ProgressSpinner from "primevue/progressspinner";

const store: any = inject("store");
const toast = useToast();

// For state
let setting_open_toggle: boolean = false;

// Vite passes the api url to here
// const api = import.meta.env.VITE_TRACTION_ENDPOINT;

const toggled = (e: any) => {
  setting_open_toggle = !e.value;
  console.log("toggled", setting_open_toggle); //why is this in the store?

  if (setting_open_toggle && !store.state.settings.self) {
    axios
      .get(`http://localhost:5100/tenant/v1/admin/self`, {
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

const make_issuer = () => {
  axios({
    method: "post",
    url: "http://localhost:5100/tenant/v1/admin/make-issuer",
    headers: {
      accept: "application/json",
      "content-type": "application/x-www-form-urlencoded",
      Authorization: `Bearer ${store.state.token}`,
    },
  })
    .then((res) => {
      toast(`Starting Issuer Process! Check back later`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
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
    <div v-else v-for="(v, k) in store.state.settings.self" :key="k">
      <span>{{ k }}:{{ typeof k }}:{{ v }} </span>
    </div>

    <Button
      label="Become an Issuer"
      v-if="store.state.settings.self.public_did_status !== 'Public'"
      @click="make_issuer"
      :disabled="store.state.settings.issuer === ''"
    ></Button>
  </Fieldset>
</template>


<script lang="ts">
export default {
  name: "TenantSettings",
};
</script>

<style></style>
