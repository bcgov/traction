<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <span class="info-card-warning">
        <i class="pi pi-exclamation-triangle info-card-icon"></i> <br />
        {{ $t('reservations.pending!') }}
      </span>
    </template>
    <template #content>
      <p>
        {{
          $t('reservations.requestReservedOn', [
            formatDateLong(reservation.created_at),
          ])
        }}
        <br />
        {{ $t('reservations.requestProcessingTime') }}
      </p>
    </template>
    <template #footer>
      <hr />
      {{ $t('reservations.checkJunkFolder') }}
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
