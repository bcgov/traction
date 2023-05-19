<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <i class="pi pi-check-circle info-card-icon"></i> <br />
      {{ $t('reservations.thankYou!') }}
    </template>
    <template #content>
      <p class="text-center">
        {{ $t('reservations.submitted') }} <br />
        {{ $t('reservations.emailSentTo', [email]) }}
      </p>
      <p v-if="pwd" class="text-center">
        {{ $t('reservations.passwordAvailable') }}
      </p>
    </template>
  </Card>

  <div class="field w-full">
    <label for="">{{ $t('common.emailAddress') }}</label>
    <InputText :value="email" type="text" readonly class="w-full" />
  </div>

  <div class="field w-full">
    <label for="">{{ $t('reservations.reservationId') }}</label>
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

  <div v-if="pwd" class="field w-full">
    <label for="">{{ $t('reservations.reservationPassword') }}</label>
    <div class="p-inputgroup">
      <InputText :value="pwd" type="text" readonly class="w-full" />
      <Button
        icon="pi pi-copy"
        title="Copy to clipboard"
        class="p-button-secondary"
        @click="copyResPwd"
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
  pwd: string;
}>();

const copyResId = () => {
  navigator.clipboard.writeText(props.id);
  toast.info('Copied Reservation Number to clipboard!');
};

const copyResPwd = () => {
  navigator.clipboard.writeText(props.pwd);
  toast.info('Copied Reservation Password to clipboard!');
};
</script>
