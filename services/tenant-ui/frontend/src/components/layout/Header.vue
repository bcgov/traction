<template>
  <Toolbar class="traction-header">
    <template #start>
      <i class="pi pi-bars p-toolbar-separator mr-2" />
    </template>

    <template #end>
      <Button icon="pi pi-search" class="p-button-text p-button-info mr-2" />
      <Button icon="pi pi-bell" class="p-button-text p-button-info mr-2" />
      <ProfileButton />
    </template>
  </Toolbar>
</template>

<script setup lang="ts">
import Toolbar from 'primevue/toolbar';
import Button from 'primevue/button';
import ProfileButton from '@/components/profile/ProfileButton.vue';
</script>
