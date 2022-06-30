<script setup lang="ts">
import { ref, inject } from "vue";
import Button from "primevue/button";
import { useToast } from "vue-toastification";
import axios from "axios";
import QRCode from "./common/QRCode.vue";
import QrcodeVue from "qrcode.vue";

// To store credentials
const alias = ref("");
const new_contact = ref("");

// For notifications
const toast = useToast();

// For state
let processing = ref(false);
let invitation = ref("");
let invitation_url = ref("");

// Grab our store
const store: any = inject("store");

const submit_new_contact = () => {
  processing.value = true; // Disable button while processing

  // const data = `username=${key.value}&password=${secret.value}`;

  axios({
    method: "post",
    url: "http://localhost:5100/tenant/v1/contacts/create-invitation",
    headers: {
      accept: "application/json",
      "content-type": "application/json",
      authorization: "Bearer " + store.state.token,
    },
    data: {
      alias: "test_alias_" + Math.floor(Math.random() * 10000000000).toString(),
    },
  })
    .then((res) => {
      invitation = res.data.invitation.toString();
      invitation_url = res.data.invitation_url;

      console.log(`invitation: ${invitation}`);
      console.log(`invitation_url: ${invitation_url}`);

      processing.value = false; // enable button
      toast(`Contact Created!`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
      processing.value = false; // enable button
    });
};
</script>

<template>
  <div class="create-contact">
    <H2>Make connection QR code</H2>
    <Button
      label="Submit"
      @click="submit_new_contact"
      :disabled="processing ? true : false"
      :loading="processing ? true : false"
    ></Button>
    <QRCode v-if="invitation_url" :qr_content="invitation_url" />
  </div>
</template>

<script lang="ts">
export default {
  name: "CreateContact",
};
</script>

<style>
.create-contact {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
