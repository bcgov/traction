<script setup lang="ts">
import { ref } from "vue";
// import InputText from "primevue/inputtext";

const key = ref("");
const secret = ref("");

const clicked = () => {
  console.log("key", key.value);
  console.log("secret", secret.value);
};

const clear = () => {
  key.value = "";
  secret.value = "";
};
</script>

<template>
  <div class="login">
    <div>
      <InputText type="text" v-model="key" placeholder="Key" />

      <input type="text" v-model="key" placeholder="Key" />
      <br />
      <input type="text" v-model="secret" placeholder="Secret" />
    </div>
    <div>
      <button @click="clear">Clear</button>
      <button @click="clicked">Submit</button>
    </div>
  </div>
</template>

<style scoped></style>
