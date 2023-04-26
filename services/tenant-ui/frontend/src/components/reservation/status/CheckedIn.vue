<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <i class="pi pi-check-circle info-card-icon"></i> <br />
      Already Complete
    </template>
    <template #content>
      <p>
        This reservation has already previously been completed and the wallet
        details given out. <br />
        The date this occurred was
        <strong> {{ formatDateLong(reservation.updated_at) }}</strong>
        <br />
        The Wallet Key cannot be retrieved again once supplied. If you require a
        new wallet you can go back and start a new reservation.
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
