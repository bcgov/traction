<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <span class="info-card-warning">
        <i class="pi pi-exclamation-triangle info-card-icon"></i> <br />
        PENDING!
      </span>
    </template>
    <template #content>
      <p>
        Your request has been received on
        {{ formatDateLong(reservation.created_at) }}. <br />
        It ususally takes 3-4 business days to process a request. Thanks for
        your patience.
      </p>
    </template>
    <template #footer>
      <hr />
      (Please check your junk/spam folder before contacting us, as it is very
      common to have the email delivery problems because of automated filters.)
    </template>
  </Card>
</template>

<script setup lang="ts">
import Card from 'primevue/card';
import { formatDateLong } from '@/helpers';
// State
import { useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';
const { reservation } = storeToRefs(useReservationStore());
</script>
