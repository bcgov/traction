<template>
  <div class="traction-sidebar">
    <h1 class="sidebar-app-title">
      <ProgressSpinner v-if="loading" />
      <span v-if="tenant">{{ tenant.tenant_name }}</span>
    </h1>
    <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
    <h1 class="sidebar-app-title small">T</h1>
    <PanelMenu :model="sidebarItems" class="mt-5">
      <template #item="{ item }">
        <PanelMenuItemLink :item="item" />
      </template>
    </PanelMenu>
  </div>
</template>

<script setup lang="ts">
import PanelMenu from 'primevue/panelmenu';
import PanelMenuItemLink from '../common/PanelMenuItemLink.vue';
import ProgressSpinner from 'primevue/progressspinner';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { useConfigStore, useTenantStore } from '../../store';

const { t } = useI18n();
const { config } = useConfigStore();
// tenant should be loaded by login...
const { tenant, loading } = storeToRefs(useTenantStore());

const sidebarItems = [
  {
    label: t('dashboard.dashboard'),
    icon: 'pi pi-fw pi-chart-bar',
    route: '/dashboard',
  },
  {
    label: t('connect.connections.connections'),
    icon: 'pi pi-fw pi-users',
    items: [
      {
        // Icons are manadatory for mobile layout
        label: t('connect.connections.connections'),
        icon: 'pi pi-fw pi-users',
        route: '/connections',
      },
      {
        label: t('connect.invitations.invitations'),
        icon: 'pi pi-fw pi-send',
        route: '/connections/invitations',
      },
    ],
  },

  {
    label: t('issue.issuance'),
    icon: 'pi pi-fw pi-credit-card',
    route: '/issuance/credentials',
  },

  {
    label: t('verify.verification'),
    icon: 'pi pi-fw pi-check-square',
    route: '/verification/verifications',
  },

  {
    label: t('common.credentials'),
    icon: 'pi pi-fw pi-wallet',
    route: '/holder/credentials',
  },

  {
    label: t('configuration.configuration'),
    icon: 'pi pi-fw pi-file',
    items: [
      {
        label: t('identifiers.identifiers'),
        icon: 'pi pi-fw pi-key text-yellow-400',
        route: '/identifiers',
      },
      {
        label: t('configuration.schemas.storage'),
        icon: 'pi pi-fw pi-book',
        route: '/schemas',
      },
      {
        label: t('configuration.credentialDefinitions.storage'),
        icon: 'pi pi-fw pi-id-card',
        route: '/credentialDefinitions',
      },
      {
        label: t('configuration.oca.oca'),
        icon: 'pi pi-fw pi-compass',
        route: '/oca',
      },
    ],
  },

  {
    label: t('messages.messages'),
    icon: 'pi pi-fw pi-envelope',
    route: '/messages/recent',
  },

  {
    label: t('about.about'),
    icon: 'pi pi-fw pi-question-circle',
    route: '/about',
  },
];

if (config?.frontend?.logStreamUrl) {
  sidebarItems.push({
    label: t('log.log'),
    icon: 'pi pi-fw pi-file',
    route: '/log',
  });
}
</script>
