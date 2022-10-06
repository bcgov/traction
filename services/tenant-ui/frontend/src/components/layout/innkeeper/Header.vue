<template>
  <Toolbar class="traction-header">
    <template #start>
      <i class="pi pi-bars p-toolbar-separator mr-2" />
    </template>

    <template #end>
      <InnkeeperBadge />
    </template>
  </Toolbar>
</template>

<script setup lang="ts">
import Toolbar from 'primevue/toolbar';
import InnkeeperBadge from '@/components/innkeeper/InnkeeperBadge.vue';
</script>
