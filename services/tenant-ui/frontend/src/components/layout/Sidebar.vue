<template>
  <div class="traction-sidebar">
    <!-- <div class="traction-sidebar" :class="calcOpen()"> -->
    <!-- <h1 v-if="tenant" class="sidebar-app-title">{{ tenant.name }}</h1> -->
    <h1 class="sidebar-app-title">Tenant UI</h1>
    <h1 class="sidebar-app-title small">T</h1>
    <PanelMenu :model="items" class="mt-5" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PanelMenu from 'primevue/panelmenu';
import { storeToRefs } from 'pinia';
import { useTenantStore } from '../../store';
import { useI18n } from 'vue-i18n';

// State
import { useGlobalStateStore } from '@/store/stateStore';

const { sidebarOpen } = storeToRefs(useGlobalStateStore());

// const calcOpen = () => {
//   // TODO: Check page width to make sure the current state of the sidebar.
//   console.log('sidebarOpen.value', sidebarOpen.value);
//   if (sidebarOpen.value === null) {
//     // Use media queries
//     return null;
//   } else if (sidebarOpen.value) {
//     // Default width
//     return 'open';
//   } else {
//     return 'closed'; // Mobile width
//   }
// };

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
    label: () => t('connect.connections'),
    icon: 'pi pi-fw pi-users',
    items: [
      {
        label: () => t('connect.connections'),
        to: { name: 'MyContacts' },
      },
      {
        label: () => t('connect.invitations.invitations'),
        to: { name: 'MyInvitations' },
      },
    ],
  },

  // {
  //   label: () => t('issue.issuance'),
  //   icon: 'pi pi-fw pi-wallet',
  //   to: { name: 'MyIssuedCredentials' },
  // },

  // {
  //   label: () => t('verify.verification'),
  //   icon: 'pi pi-fw pi-check-square',
  //   to: { name: 'MyPresentations' },
  // },

  // {
  //   label: () => t('holder.holder'),
  //   icon: 'pi pi-fw pi-id-card',
  //   to: { name: 'MyHeldCredentials' },
  // },

  {
    label: () => t('messages.messages'),
    icon: 'pi pi-fw pi-envelope',
    to: { name: 'MyMessages' },
  },

  // {
  //   label: () => t('configuration.configuration'),
  //   icon: 'pi pi-fw pi-file',
  //   items: [
  //     {
  //       label: () => t('configuration.schemasCreds.schemas'),
  //       to: { name: 'Schemas' },
  //     },
  //     {
  //       label: () => t('configuration.presentationTemplates.templates'),
  //       to: { name: 'PresentationTemplates' },
  //     },
  //   ],
  // },

  {
    label: () => t('about.about'),
    icon: 'pi pi-fw pi-question-circle',
    to: { name: 'About' },
  },
]);
</script>

<style scoped>
.sidebar-app-title.small {
  display: none;
  font-size: 2rem;
}
/* media queries */
@media (max-width: 100rem) {
  :deep(.p-menuitem-text) {
    display: none;
  }
  :deep(.p-menuitem-icon) {
    font-size: 2rem !important;
    margin-left: 0.5rem;
  }
  .sidebar-app-title {
    display: none;
  }
  .sidebar-app-title.small {
    display: block;
  }
}
</style>
