<template>
  <div>
    <Button
      :label="$t('connect.didExchange.didExchange')"
      icon="pi pi-arrows-h"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :style="{ minWidth: '400px' }"
      :header="$t('connect.didExchange.didExchange')"
      :modal="true"
      @update:visible="handleClose"
    >
      <DidExchangeForm @success="$emit('success')" @closed="handleClose" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// Custom Components
import DidExchangeForm from './DidExchangeForm.vue';
// Other Imports

defineEmits(['success']);

const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs (if needed)
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
</script>
