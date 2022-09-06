<script setup lang="ts">
import ConfirmPopup from 'primevue/confirmpopup';
import AppLayout from './components/layout/AppLayout.vue';
import Login from './components/Login.vue';
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useConfigStore, useTenantStore } from './store';

const { config } = storeToRefs(useConfigStore());
const { tenantReady } = storeToRefs(useTenantStore());

onMounted(() => {
  document.title = config.value.ux.appTitle;
});
</script>

<template>
  <AppLayout v-if="tenantReady" />
  <Login v-else />

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
