<template>
  <Button
    title="Edit Connection"
    icon="pi pi-pencil"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="openModal"
  />
  <Dialog
    v-model:visible="displayModal"
    :style="{ minWidth: '500px' }"
    header="Edit Connection"
    :modal="true"
    @update:visible="handleClose"
  >
    <EditConnectionForm
      :connection-id="props.connectionId"
      @closed="handleClose"
    />
  </Dialog>
</template>

<script setup lang="ts">
// Vue
import { ref, PropType } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// Custom Components
import EditConnectionForm from './EditConnectionForm.vue';

// Props
const props = defineProps({
  connectionId: {
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
