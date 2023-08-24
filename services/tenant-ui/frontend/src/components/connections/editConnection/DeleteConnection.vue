<template>
  <Button
    title="Delete Connection"
    icon="pi pi-trash"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="deleteConnection($event)"
  />
</template>

<script setup lang="ts">
// Vue
import { PropType } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useConnectionStore } from '@/store';

const confirm = useConfirm();
const toast = useToast();

const connectionStore = useConnectionStore();

// Props
const props = defineProps({
  connectionId: {
    type: String as PropType<string>,
    required: true,
  },
});

// Delete the connection record by connection id
const deleteConnection = (event: any) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this connection?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete();
    },
  });
};
const doDelete = () => {
  connectionStore
    .deleteConnection(props.connectionId)
    .then(() => {
      toast.success(`Connection successfully deleted`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};
</script>
