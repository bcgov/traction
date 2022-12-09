<template>
  <Card class="info-card mt-4">
    <template #title>
      <i class="pi pi-check-circle info-card-icon"></i> <br />
      Thank You!
    </template>
    <template #content>
      <p class="text-center">
        Your request has been submitted successfully. <br />
        An email has also been sent to sdflkjsdflkjs with the reservation number
        below.
      </p>
    </template>
  </Card>
</template>

<script setup lang="ts">
// Vue
import { ref, reactive } from 'vue';
// PrimeVue/Validation/etc
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
</script>
