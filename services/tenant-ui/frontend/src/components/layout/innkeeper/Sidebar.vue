<template>
  <div class="traction-sidebar innkeeper-sidebar">
    <h1 class="sidebar-app-title">Innkeeper</h1>
    <PanelMenu :model="items" class="mt-5" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PanelMenu from 'primevue/panelmenu';

const items = ref([
  {
    label: 'Tenants',
    icon: 'pi pi-fw pi-users',
    to: { name: 'InnkeeperTenants' },
  },
  {
    label: 'About',
    icon: 'pi pi-fw pi-question-circle',
    to: { name: 'InnkeeperAbout' },
  },
]);
</script>
