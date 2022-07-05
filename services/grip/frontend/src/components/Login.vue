<script setup lang="ts">
import { ref, inject } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import { useToast } from "vue-toastification";
import axios from "axios";

// To store credentials
const key = ref("");
const secret = ref("");

// For notifications
const toast = useToast();

// For state
let processing = ref(false);

// Grab our store
const store: any = inject("store");

/**
 * ##clicked
 * Read the form, formulate the request url then
 * request token from API
 */
const clicked = () => {
  processing.value = true; // Disable button while processing

  const data = `username=${key.value}&password=${secret.value}`;

  axios({
    method: "post",
    url: "http://localhost:5100/tenant/token",
    headers: {
      accept: "application/json",
      "content-type": "application/x-www-form-urlencoded",
    },
    data: data,
  })
    .then((res) => {
      const token = res.data.access_token;
      processing.value = false; // enable button
      console.log(`Access Token: ${token}`);
      store.state.token = token;
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
      processing.value = false; // enable button
      store.state.token = null;
    });
};

/**
 * ## clear
 * Clear the form
 */
const clear = () => {
  key.value = "";
  secret.value = "";
};
</script>

<template>
  <div class="login">
    <div>
      <span class="p-float-label">
        <InputText
          type="text"
          v-model="key"
          autocomplete="username"
          name="username"
          autofocus
        />
        <label for="key">Wallet ID</label>
      </span>

      <span class="p-float-label">
        <InputText
          type="password"
          autocomplete="current-password"
          v-model="secret"
          name="password"
        />
        <label for="secret">Wallet Key</label>
      </span>
    </div>
    <div>
      <Button label="Clear" class="p-button-warning" @click="clear"></Button>
      <Button
        label="Submit"
        @click="clicked"
        :disabled="processing ? true : false"
        :loading="processing ? true : false"
      ></Button>
    </div>
  </div>
</template>

<style scoped>
span.p-float-label {
  margin: 25px;
}
button {
  margin: 0 20px;
}
</style>
