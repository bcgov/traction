<script setup lang="ts">
import { inject } from "vue";
import Fieldset from "primevue/fieldset";
import Card from "primevue/card";
import ProgressSpinner from "primevue/progressspinner";
import axios from "axios";

const store: any = inject("store");

// Vite passes the api url to here
const api = import.meta.env.VITE_TRACTION_ENDPOINT;

const toggled = (e: any) => {
  store.state.walletInfo.open = !e.value;
  if (store.state.walletInfo.open && !store.state.walletInfo.data) {
    axios
      .get(`${api}/tenant/v1/admin/self`, {
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${store.state.token}`,
        },
      })
      .then((res) => {
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

    <!--
      If there is no data, show a spinner.
      Otherwise show the data.
    -->
    <ProgressSpinner v-if="!store.state.walletInfo.data" />
    <div v-else>
      <card>
        <template #title>{{ store.state.walletInfo.data.name }}</template>
        <template #content>
          <div>
            <span>Tenant ID: &nbsp;</span>
            <span>{{ store.state.walletInfo.data.tenant_id }}</span>
          </div>
          <div>
            <span>Wallet ID: &nbsp;</span>
            <span>{{ store.state.walletInfo.data.wallet_id }}</span>
          </div>
          <div>
            <span>Issuer: &nbsp;</span>
            <span>{{ store.state.walletInfo.data.issuer }}</span>
          </div>
          <div>
            <span>Issuer Status: &nbsp;</span>
            <span>{{ store.state.walletInfo.data.issuer_status }}</span>
          </div>
          <div>
            <span>Public DID: &nbsp;</span>
            <span>{{ store.state.walletInfo.data.public_did }}</span>
          </div>
          <div>
            <span>Public DID Status: &nbsp;</span>
            <span>{{ store.state.walletInfo.data.public_did_status }}</span>
          </div>
          <div>
            <span>Date Created: &nbsp;</span>
            <span>{{ store.state.walletInfo.data.created_at }}</span>
          </div>
          <div>
            <span>Date Last Updated: &nbsp;</span>
            <span>{{ store.state.walletInfo.data.updated_at }}</span>
          </div>
          <div>
            <span>Deleted: &nbsp;</span>
            <span>{{ store.state.walletInfo.data.deleted }}</span>
          </div>
        </template>
      </card>
    </div>
  </Fieldset>
</template>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
