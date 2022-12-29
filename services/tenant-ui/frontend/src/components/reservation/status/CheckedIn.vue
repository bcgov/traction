<template>
  <Card class="info-card mt-4 mb-6">
    <template #title>
      <i class="pi pi-check info-card-icon"></i> <br />
      Already done
    </template>
    <template #content>
      The tenant has already checked in and been shown their wallet details. UX
      here TBD
    </template>
    <template #footer>
      <hr />
      Any text here TBD
    </template>
  </Card>
</template>

<script setup lang="ts">
// PrimeVue
import Card from 'primevue/card';
</script>
