<template>
  <Toolbar class="traction-header">
    <template #start>
      <i class="pi pi-bars p-toolbar-separator mr-2" />
    </template>

    <template #end>
      <LocaleSwitcher />

      <ProfileButton />
    </template>
  </Toolbar>
</template>

<script setup lang="ts">
import Toolbar from 'primevue/toolbar';
import ProfileButton from '@/components/profile/ProfileButton.vue';
import LocaleSwitcher from '../common/LocaleSwitcher.vue';
</script>
