<template>
  <Button
    title="Delete Presentation Exchange Record"
    icon="pi pi-trash"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="deleteRecord($event)"
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
import { useVerifierStore } from '@/store';

const confirm = useConfirm();
const toast = useToast();

const verifierStore = useVerifierStore();

// Props
const props = defineProps({
  recordId: {
    type: String as PropType<string>,
    required: true,
  },
});

// Delete the connection record by connection id
const deleteRecord = (event: any) => {
  confirm.require({
    target: event.currentTarget,
    message:
      'Are you sure you want to delete this Presentation Exchange Record?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete();
    },
  });
};
const doDelete = () => {
  verifierStore
    .deleteRecord(props.recordId)
    .then(() => {
      toast.success(`Presentation Exchange Record successfully deleted`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};
</script>
