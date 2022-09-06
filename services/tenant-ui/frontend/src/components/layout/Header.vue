<template>
  <Toolbar class="traction-header">
    <template #start>
      <i class="pi pi-bars p-toolbar-separator mr-2" />
      <Issuance />
    </template>

    <template #end>
      <Button icon="pi pi-search" class="p-button-text p-button-info mr-2" />
      <Button icon="pi pi-bell" class="p-button-text p-button-info mr-2" />
      <Button icon="pi pi-user" class="p-button-icon p-button-rounded" />
    </template>
  </Toolbar>
</template>

<script setup lang="ts">
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import Issuance from '@/components/common/Issuance.vue';
</script>

<style>
/* spamming important here. TODO: figure out best way to override this with theme */
.p-toolbar {
  background-color: white !important;
  padding: 0.5em !important;
  border-radius: 0 !important;
}
</style>
