<template>
  <div class="traction-sidebar">
    <h1 v-if="tenant" class="sidebar-app-title">{{ tenant.name }}</h1>
    <!--<h1 class="sidebar-app-title">{{ config.ux.sidebarTitle }}</h1>-->
    <PanelMenu :model="items" class="mt-5" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PanelMenu from 'primevue/panelmenu';
import { storeToRefs } from 'pinia';
import { useTenantStore } from '../../store';

// tenant should be loaded by login...
const { tenant } = storeToRefs(useTenantStore());

const items = ref([
  {
    label: 'Dashboard',
    icon: 'pi pi-fw pi-chart-bar',
    to: { name: 'Dashboard' },
  },
  {
    label: 'Contacts',
    icon: 'pi pi-fw pi-users',
    to: { name: 'MyContacts' },
  },

  {
    label: 'Issuance',
    icon: 'pi pi-fw pi-wallet',
    to: { name: 'MyIssuedCredentials' },
  },

  {
    label: 'Verification',
    icon: 'pi pi-fw pi-check-square',
    to: { name: 'MyPresentations' },
  },

  {
    label: 'Holder',
    icon: 'pi pi-fw pi-id-card',
    to: { name: 'MyHeldCredentials' },
  },

  {
    label: 'Configuration',
    icon: 'pi pi-fw pi-file',
    items: [
      {
        label: 'Schemas',
        to: { name: 'Schemas' },
      },
      {
        label: 'Presentation Templates',
        to: { name: 'PresentationTemplates' },
      },
    ],
  },

  {
    label: 'About',
    icon: 'pi pi-fw pi-question-circle',
    to: { name: 'About' },
  },
]);
</script>
