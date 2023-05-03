<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <span class="info-card-danger">
        <i class="pi pi-times-circle info-card-icon"></i> <br />
        {{ $t('reservations.declined!') }}
      </span>
    </template>
    <template #content>
      <p>{{ $t('reservations.requestDeclined') }}</p>
      <div v-if="reservation.state_notes">
        <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
        {{ $t('reservations.resonForRejection') }}: <br />
        <pre>{{ reservation.state_notes }}</pre>
      </div>
      <p>
        {{ $t('reservations.submitNewRequest') }}
      </p>
    </template>
  </Card>
</template>

<script setup lang="ts">
import Card from 'primevue/card';
// State
import { useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';
const { reservation } = storeToRefs(useReservationStore());
</script>
