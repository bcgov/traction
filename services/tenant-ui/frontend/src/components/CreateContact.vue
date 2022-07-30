<script setup lang="ts">
import { ref, inject } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import { useToast } from 'primevue/usetoast';
import axios from "axios";
import QRCode from "./common/QRCode.vue";

// To store credentials
const create_contact_alias = ref("");

// For notifications
const toast = useToast();

// For state
let processing = ref(false);
let invitation_url = ref("");

// Grab our store
const store: any = inject("store");

const submit_new_contact = () => {
  processing.value = true; // Disable button while processing

  // const data = `username=${key.value}&password=${secret.value}`;

  axios({
    method: "post",
    url: "api/traction/tenant/v1/contacts/create-invitation",
    headers: {
      accept: "application/json",
      "content-type": "application/json",
      authorization: "Bearer " + store.state.token,
    },
    data: {
      alias: create_contact_alias.value,
    },
  })
    .then((res) => {
      invitation_url.value = res.data.invitation_url;
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
    <h1>Contacts</h1>
    <div>
      <h2>Create Connection Invitation</h2>
      <span class="p-float-label">
        <InputText type="text" v-model="create_contact_alias" name="create_contact_alias" autofocus />
        <label for="create_contact_alias">Contact Alias</label>
      </span>
    </div>
    <QRCode v-if="invitation_url" :qr_content="invitation_url" />
    <Button v-else label="Submit" @click="submit_new_contact" :disabled="processing ? true : false"
      :loading="processing ? true : false"></Button>
  </div>
</template>

<style scoped>
.create-contact {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  margin: 10px;
  padding: 15px;
  border: 3px solid grey;
  border-radius: 8px;
}

span.p-float-label {
  margin: 25px;
}
</style>
