<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <i class="pi pi-check-circle info-card-icon"></i> <br />
      {{ $t('reservations.alreadyComplete') }}
    </template>
    <template #content>
      <p>
        {{ $t('reservations.reservationPreviouslyCompleted') }} <br />
        {{
          $t('reservations.dateOccurred', [
            formatDateLong(reservation.updated_at),
          ])
        }}
        <br />
        {{ $t('reservations.walletKeyCannotBeRetrievedAgain') }}
      </p>
    </template>
  </Card>
</template>

<script setup lang="ts">
import Card from 'primevue/card';
import { formatDateLong } from '@/helpers';
import { useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';
const { reservation } = storeToRefs(useReservationStore());
</script>
