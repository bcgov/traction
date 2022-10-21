<template>
  <Button
    title="Edit Contact"
    icon="pi pi-pencil"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="openModal"
  />
  <Dialog
    v-model:visible="displayModal"
    header="Edit Contact"
    :modal="true"
    @update:visible="handleClose"
  >
    <EditContactForm :contactId="props.contactId" @closed="handleClose" />
  </Dialog>
</template>

<script setup lang="ts">
// Vue
import { ref, PropType } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// Custom Components
import EditContactForm from './EditContactForm.vue';

// Props
const props = defineProps({
  contactId: {
    type: String as PropType<string>,
    required: true,
  },
});

const displayModal = ref(false);
const openModal = async () => {
  displayModal.value = true;
};
const handleClose = async () => {
  displayModal.value = false;
};
</script>

<style lang="scss" scoped>
.p-dialog {
  min-width: 400px;
}
</style>
