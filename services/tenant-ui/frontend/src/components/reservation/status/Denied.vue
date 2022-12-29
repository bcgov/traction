<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <span class="info-card-danger">
        <i class="pi pi-times-circle info-card-icon"></i> <br />
        DECLINED!
      </span>
    </template>
    <template #content>
      <p>We regret to inform you that your request has been declined.</p>
      <div v-if="reservation.state_notes">
        Reason for rejection: <br />
        <pre>{{ reservation.state_notes }}</pre>
      </div>
      <p>
        If you think there has been an error you can submit a new request again.
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
