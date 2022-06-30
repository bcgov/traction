<script setup lang="ts">
import Login from "./components/Login.vue";
import TenantDashboard from "./components/TenantDashboard.vue";

import store from "./store";
import { provide } from "vue";

provide("store", store); // Allow the entire app to see the store.
</script>

<template>
  <Login v-if="!store.state.token" />
  <TenantDashboard v-else />
</template>

<style>
html,
body {
  height: 100%;
}
#app {
  height: 100%;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
.login {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>

