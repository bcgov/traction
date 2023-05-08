<template>
  <div>
    <Button
      :label="$t('messages.createMessage')"
      icon="pi pi-envelope"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="$t('messages.createMessage')"
      :modal="true"
      :style="{ width: '500px' }"
      @update:visible="handleClose"
    >
      <CreateMessageForm @success="$emit('success')" @closed="handleClose" />
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
import CreateMessageForm from './CreateMessageForm.vue';

defineEmits(['success']);

const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
</script>
