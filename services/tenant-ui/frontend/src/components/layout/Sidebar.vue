<template>
  <div>
    <h1 class="sidebar-app-title">{{ tenant.name }}</h1>
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

<style scoped lang="scss">
.sidebar-app-title {
  font-size: 1.6em;
  text-align: center;
  padding: 0.5em;
  margin: 0.5em;
  background-color: $tenant-ui-accent-color;
  text-transform: uppercase;
  word-wrap: break-word;
}

.p-panelmenu {
  :deep(.p-panelmenu-panel) {
    * {
      background-color: $tenant-ui-primary-color !important;
      border: none !important;
      color: $tenant-ui-text-on-primary !important;
      font-weight: normal !important;
    }
    .p-submenu-list {
      padding-left: 1.5em !important;
    }
    // Override the order of the drop down icon
    .p-panelmenu-header-link {
      display: flex;
      span {
        &.pi-chevron-right,
        &.pi-chevron-down {
          order: 2;
          margin-left: auto;
        }
      }
    }
  }
}
</style>
