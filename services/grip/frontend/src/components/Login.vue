<script setup lang="ts">
import { defineComponent, ref } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
// import axios from "axios";

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
      <span class="p-float-label">
        <InputText type="text" v-model="key" />
        <label for="key">Key</label>
      </span>

      <span class="p-float-label">
        <InputText type="text" v-model="secret" />
        <label for="secret">Secret</label>
      </span>
    </div>
    <div>
      <Button label="Clear" class="p-button-warning" @click="clear"></Button>
      <Button label="Submit" @click="clicked"></Button>
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
