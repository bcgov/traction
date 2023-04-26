<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <i class="pi pi-check-circle info-card-icon"></i> <br />
      Thank You!
    </template>
    <template #content>
      <p class="text-center">
        Your request has been submitted successfully. <br />
        An email has also been sent to {{ email }} with the reservation number
        below.
      </p>
    </template>
  </Card>

  <div class="field w-full">
    <label for="">Email Address</label>
    <InputText :value="email" type="text" readonly class="w-full" />
  </div>

  <div class="field w-full">
    <label for="">Reservation Number</label>
    <div class="p-inputgroup">
      <InputText :value="id" type="text" readonly class="w-full" />
      <Button
        icon="pi pi-copy"
        title="Copy to clipboard"
        class="p-button-secondary"
        @click="copyResId"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// PrimeVue/Validation/etc
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import { useToast } from 'vue-toastification';
const toast = useToast();

const props = defineProps<{
  email: string;
  id: string;
}>();

const copyResId = () => {
  navigator.clipboard.writeText(props.id);
  toast.info('Copied Reservation Number to clipboard!');
};
</script>
