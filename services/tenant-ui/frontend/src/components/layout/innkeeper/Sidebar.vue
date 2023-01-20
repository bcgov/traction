<template>
  <div class="traction-sidebar innkeeper-sidebar">
    <h1 class="sidebar-app-title">Innkeeper</h1>
    <h1 class="sidebar-app-title small">I</h1>
    <PanelMenu :model="items" class="mt-5" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PanelMenu from 'primevue/panelmenu';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const items = ref([
  {
    label: () => t('reservations.reservations'),
    icon: 'pi pi-fw pi-book',
    items: [
      {
        label: () => t('reservations.current'),
        to: { name: 'InnkeeperReservations' },
      },
      {
        label: () => t('reservations.history'),
        to: { name: 'InnkeeperReservationsHistory' },
      },
    ],
  },
  {
    label: () => t('tenants.tenants'),
    icon: 'pi pi-fw pi-users',
    to: { name: 'InnkeeperTenants' },
  },
  {
    label: () => t('about.about'),
    icon: 'pi pi-fw pi-question-circle',
    to: { name: 'InnkeeperAbout' },
  },
]);
</script>
