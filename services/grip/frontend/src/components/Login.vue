<script setup lang="ts">
import { ref } from "vue";
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

const clicked = () => {
  processing.value = true; // Disable button while processing
  toast(`${key.value} ${secret.value}`);
};

const clear = () => {
  key.value = "";
  secret.value = "";
};
</script>

<template>
  <div class="login">
    <div>
      <span class="p-float-label">
        <InputText type="text" v-model="key" />
        <label for="key">Wallet ID</label>
      </span>

      <span class="p-float-label">
        <InputText type="text" v-model="secret" />
        <label for="secret">Wallet Key</label>
      </span>
    </div>
    <div>
      <Button label="Clear" class="p-button-warning" @click="clear"></Button>
      <Button
        label="Submit"
        @click="clicked"
        :disabled="processing ? true : false"
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
