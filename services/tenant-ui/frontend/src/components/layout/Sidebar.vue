<template>
  <div>
    <h1 class="sidebar-app-title">{{ tenant.name }}</h1>
    <!--<h1 class="sidebar-app-title">{{ config.ux.sidebarTitle }}</h1>-->
    <PanelMenu :model="items" class="mt-5" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import PanelMenu from 'primevue/panelmenu';
import { storeToRefs } from 'pinia';
import { useTenantStore } from '../../store';

const tenantStore = useTenantStore();
// tenant should be loaded by login...
const { tenant } = storeToRefs(useTenantStore());

const items = ref([
  {
    label: 'Dashboard',
    icon: 'pi pi-fw pi-chart-bar',
    to: { name: 'Dashboard' },
  },
  {
    label: 'Connections',
    icon: 'pi pi-fw pi-users',
    items: [
      {
        label: 'My Contacts',
        to: { name: 'MyContacts' },
      },
      {
        label: 'Accept Invitation',
        to: { name: 'AcceptInvitation' },
      },
    ],
  },

  {
    label: 'Issuance',
    icon: 'pi pi-fw pi-wallet',
    items: [
      {
        label: 'Schemas',
        to: { name: 'Schemas' },
      },
      {
        label: 'My Issued Credentials',
        to: { name: 'MyIssuedCredentials' },
      },
    ],
  },

  {
    label: 'Verification',
    icon: 'pi pi-fw pi-check-square',
    items: [
      {
        label: 'My Presentations',
        to: { name: 'MyPresentations' },
      },
      {
        label: 'Create A Presentation Request',
        to: { name: 'CreatePresentation' },
      },
      {
        label: 'Presentation Templates',
        to: { name: 'PresentationTemplates' },
      },
    ],
  },

  {
    label: 'Holder',
    icon: 'pi pi-fw pi-key',
    items: [
      {
        label: 'My Held Credentials',
        to: { name: 'MyHeldCredentials' },
      },
      {
        label: 'Accept a Credential Offer',
        to: { name: 'AcceptCredential' },
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

<style>
.sidebar-app-title {
  font-size: 1.6em;
  text-align: center;
  padding: 0.5em 1.7em;
  margin: 0.5em;
  background-color: #96c230;
  text-transform: uppercase;
}

/* TODO: quick and dirty, rewrite this (or better, find theme settings) */
.p-panelmenu,
.p-panelmenu-panel > .p-panelmenu-header > a > *,
.p-panelmenu,
.p-panelmenu-panel > .p-panelmenu-header > a,
.p-panelmenu-content,
.p-submenu-list > *,
.p-menuitem-link > *,
a.p-menuitem-link:hover {
  background-color: #244075 !important;
  border: none !important;
  color: white !important;
  font-weight: normal !important;
}
</style>
