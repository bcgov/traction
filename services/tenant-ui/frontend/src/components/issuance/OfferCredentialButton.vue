<template>
  <div>
    <Button label="Show" icon="pi pi-external-link" @click="openOfferPopup" />
    <Dialog header="Header" v-model:visible="displayOfferModal" :modal="true">
      <p class="m-0">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore
        et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
        laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
        cillum dolore eu fugiat nulla pariatur.
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
      </p>
      <template #footer>
        <Button label="No" icon="pi pi-times" @click="displayOfferModal = false" class="p-button-text" />
        <Button label="Yes" icon="pi pi-check" @click="displayOfferModal = false" autofocus />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref } from "vue";

// PrimeVue
import Button from "primevue/button";
import Dialog from "primevue/dialog";

// Other Imports
import { useToast } from "vue-toastification";

// ----------------------------------------------------------------
// Display popup
// ----------------------------------------------------------------
const displayOfferModal = ref(false);
const openOfferPopup = () => {
  displayOfferModal.value = true;
};
// -------------------------------------------------------/display
</script>
