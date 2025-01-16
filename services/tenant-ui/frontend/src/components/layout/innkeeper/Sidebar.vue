<template>
  <div class="traction-sidebar innkeeper-sidebar">
    <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
    <h1 class="sidebar-app-title">Innkeeper</h1>
    <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
    <h1 class="sidebar-app-title small">I</h1>
    <PanelMenu :model="items" class="mt-5">
      <template #item="{ item }">
        <PanelMenuItemLink :item="item" />
      </template>
    </PanelMenu>
  </div>
</template>

<script setup lang="ts">
import PanelMenu from 'primevue/panelmenu';
import { useI18n } from 'vue-i18n';
import PanelMenuItemLink from '@/components/common/PanelMenuItemLink.vue';
import { useConfigStore } from '../../../store';

const { t } = useI18n();
const { config } = useConfigStore();

const ROOT = '/innkeeper/';
const items = [
  {
    label: t('reservations.reservations'),
    icon: 'pi pi-fw pi-book',
    items: [
      {
        // Icons are manadatory for mobile layout
        label: t('reservations.current'),
        icon: 'pi pi-fw pi-calendar',
        route: ROOT + 'reservations',
      },
      {
        label: t('reservations.history'),
        icon: 'pi pi-fw pi-history',
        route: ROOT + 'reservations/history',
      },
    ],
  },
  {
    label: t('tenants.tenants'),
    icon: 'pi pi-fw pi-users',
    route: ROOT + 'tenants',
  },
  {
    label: t('apiKey.apiKeys'),
    icon: 'pi pi-fw pi-key',
    route: ROOT + 'authentications/keys',
  },
  {
    label: t('serverConfig.serverConfig'),
    icon: 'pi pi-fw pi-wrench',
    route: ROOT + 'server',
  },
  {
    label: t('about.about'),
    icon: 'pi pi-fw pi-question-circle',
    route: ROOT + 'about',
  },
];

if (config?.frontend?.logStreamUrl) {
  items.push({
    label: t('log.log'),
    icon: 'pi pi-fw pi-file',
    route: ROOT + 'log',
  });
}
</script>
<style scoped lang="scss">
.sidebar-app-title.small {
  position: relative;
  left: -0.5rem;
  width: 3.2rem;
  padding-left: 1.4rem;
  padding-right: 1.4rem;
}
</style>
