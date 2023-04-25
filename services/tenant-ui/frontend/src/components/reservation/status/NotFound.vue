<template>
  <Message severity="error" :closable="false">
    {{ $t('reservations.incorrectEmailOrReservationId') }}
  </Message>
</template>
<script setup lang="ts">
import Message from 'primevue/message';
</script>
