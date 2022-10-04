<script setup lang="ts">
import ConfirmPopup from 'primevue/confirmpopup';
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useConfigStore } from './store';

const { config } = storeToRefs(useConfigStore());

onMounted(() => {
  document.title = config.value.ux.appTitle;
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
