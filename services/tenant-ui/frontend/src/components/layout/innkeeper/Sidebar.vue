<template>
  <div>
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
    icon: 'pi pi-fw pi-chart-bar',
    to: { name: 'InnkeeperTenants' },
  },
  {
    label: 'About',
    icon: 'pi pi-fw pi-question-circle',
    to: { name: 'InnkeeperAbout' },
  },
]);
</script>

<!-- Extract this up to global if the innkeeper sidebar ends up being the same style as tenant -->
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
      .p-menuitem-icon {
        font-size: 1.3em;
      }
    }
  }
}
</style>
