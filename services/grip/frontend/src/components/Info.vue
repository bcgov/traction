<script setup lang="ts">
import { inject } from "vue";
import { useToast } from "vue-toastification";
import Button from "primevue/button";
import Fieldset from "primevue/fieldset";
import Card from "primevue/card";
import ProgressSpinner from "primevue/progressspinner";
import axios from "axios";

const store: any = inject("store");
const toast = useToast();

// Vite passes the api url to here
const api = import.meta.env.VITE_TRACTION_ENDPOINT;

const make_issuer = () => {
  axios({
    method: "post",
    url: `${api}/tenant/v1/admin/make-issuer`,
    headers: {
      accept: "application/json",
      "content-type": "application/x-www-form-urlencoded",
      Authorization: `Bearer ${store.state.token}`,
    },
  })
    .then(() => {
      toast(`Starting Issuer Process! Check back later`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};

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
      <Button
        label="Become an Issuer"
        v-if="store.state.walletInfo.data.public_did_status === 'N/A'"
        @click="make_issuer"
      ></Button>
      <Button label="Already an Issuer" v-else :disabled="true"></Button>
    </div>
  </Fieldset>
</template>

<style scoped>
fieldset {
  display: flex;
  align-items: center;
  justify-content: center;
}

button {
  margin-top: 10px;
}
</style>
