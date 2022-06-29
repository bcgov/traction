<script setup lang="ts">
import { inject } from "vue";
import Fieldset from "primevue/fieldset";
import ProgressSpinner from "primevue/progressspinner";
import axios from "axios";

const store: any = inject("store");

// Vite passes the api url to here
const api = import.meta.env.VITE_TRACTION_ENDPOINT;

const toggled = () => {
  console.log("toggled");
};
</script>

<template>
  <Fieldset
    :toggleable="true"
    :collapsed="!store.state.contacts.open"
    @toggle="toggled"
  >
    <template #legend>Contacts</template>
  </Fieldset>
</template>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
