<template>
  <div class="traction-sidebar">
    {{ someProperty }}
    <h1 v-if="tenant" class="sidebar-app-title">{{ tenant.name }}</h1>
    <!--<h1 class="sidebar-app-title">{{ config.ux.sidebarTitle }}</h1>-->
    <PanelMenu :model="items" class="mt-5" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import PanelMenu from 'primevue/panelmenu';
import { storeToRefs } from 'pinia';
import { useTenantStore } from '../../store';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// tenant should be loaded by login...
const { tenant } = storeToRefs(useTenantStore());

const items = ref([
  {
    label: () => t('home.dashboard'),
    icon: 'pi pi-fw pi-chart-bar',
    to: { name: 'Dashboard' },
  },
  {
    label: () => t('contact.contacts'),
    icon: 'pi pi-fw pi-users',
    to: { name: 'MyContacts' },
  },

  {
    label: 'Issuance',
    label: () => t('home.dashboard'),
    icon: 'pi pi-fw pi-wallet',
    to: { name: 'MyIssuedCredentials' },
  },

  {
    label: 'Verification',
    label: () => t('home.dashboard'),
    icon: 'pi pi-fw pi-check-square',
    to: { name: 'MyPresentations' },
  },

  {
    label: 'Holder',
    label: () => t('home.dashboard'),
    icon: 'pi pi-fw pi-id-card',
    to: { name: 'MyHeldCredentials' },
  },

  {
    label: 'Messages',
    icon: 'pi pi-fw pi-envelope',
    to: { name: 'MyMessages' },
  },

  {
    label: 'Configuration',
    label: () => t('home.dashboard'),
    icon: 'pi pi-fw pi-file',
    items: [
      {
        label: 'Schemas',
        label: () => t('home.dashboard'),
        to: { name: 'Schemas' },
      },
      {
        label: 'Presentation Templates',
        label: () => t('home.dashboard'),
        to: { name: 'PresentationTemplates' },
      },
    ],
  },

  {
    label: 'About',
    label: () => t('home.dashboard'),
    icon: 'pi pi-fw pi-question-circle',
    to: { name: 'About' },
  },
]);
</script>
