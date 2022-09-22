<!--
  For "Super" users... that means you fellow Dev. This tool allows
  for easy interactions with the API without going through
  Swagger or messing around with Curl.
-->
<template>
  <Button
    icon="pi pi-bolt"
    class="p-button-rounded p-button-outlined"
    title="Custom API Call"
    @click="toggleModal"
  ></Button>
  <Dialog
    v-model:visible="displayModal"
    header="Custom API Call"
    :modal="true"
  />
</template>
<script setup lang="ts">
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { ref } from 'vue';

const displayModal = ref(false);

const toggleModal = () => {
  console.log('toggleModal');
  displayModal.value
    ? (displayModal.value = false)
    : (displayModal.value = true);
};
</script>
<style></style>
