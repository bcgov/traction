<script setup lang="ts">
import { storeToRefs } from 'pinia';
import ConfirmPopup from 'primevue/confirmpopup';
import { onMounted } from 'vue';
import {
  useConfigStore,
  useInnkeeperTokenStore,
  useTenantStore,
  useTokenStore,
} from './store';

const { config } = storeToRefs(useConfigStore());

onMounted(() => {
  document.title = config.value.frontend.ux.appTitle;

  // This is used to remove localStorage data when the user driectly accesses the app as a new window or tab.
  // The token is still in the browser localstorage before this, so it is a superficial security measure.
  if (sessionStorage.getItem('reloaded') == null) {
    if (window.location.href.includes('/innkeeper'))
      useInnkeeperTokenStore().clearToken();
    else {
      useTokenStore().clearToken();
      useTenantStore().clearTenant();
    }
  }

  sessionStorage.setItem('reloaded', 'true');
});
</script>

<template>
  <router-view />

  <!-- Shared confirm popup  -->
  <ConfirmPopup />
</template>

<style scoped>
#app {
  height: 100%;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
