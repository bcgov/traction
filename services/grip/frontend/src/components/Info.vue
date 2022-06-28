<script setup lang="ts">
import { inject } from "vue";
import Fieldset from "primevue/fieldset";
import ProgressSpinner from "primevue/progressspinner";
import axios from "axios";

const store: any = inject("store");

const toggled = (e: any) => {
  console.log("toggled");
  store.state.walletInfo.open = !e.value;
  if (store.state.walletInfo.open && !store.state.walletInfo.data) {
    console.log("Fetching wallet info");
    axios
      .get("http://localhost:5100/tenant/v1/admin/self", {
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${store.state.token}`,
        },
      })
      .then((res) => {
        console.log("res", res);
        store.state.walletInfo.data = res.data.item;
      })
      .catch((err) => {
        store.state.walletInfo.data = null;
        console.error("error", err);
      });
  }
};
</script>

<template>
  <Fieldset
    :toggleable="true"
    :collapsed="!store.state.walletInfo.open"
    @toggle="toggled"
  >
    <template #legend> Wallet Info </template>
    <!-- Token: {{ store.state.token }} -->
    <ProgressSpinner v-if="!store.state.walletInfo.data" />
    <div v-else>hey there</div>
  </Fieldset>
</template>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
