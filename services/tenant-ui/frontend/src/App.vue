<script setup lang="ts">
import ApiHealth from "./components/ApiHealth.vue";
import Dashboard from "./pages/Dashboard.vue";
import Login from "./components/Login.vue";
import store from "./store";
import { inject, provide } from "vue";

let globalVar = inject('config')
provide("store", store); // Allow the entire app to see the store.

</script>

<template>
  <h2>Config from backend</h2>
  {{ globalVar }}

  <hr />
  <h2>Vue Routing structure</h2>
  <div id="nav">
    <router-link to="/">Home</router-link> |
    <router-link to="/about">About</router-link>
  </div>
  <router-view />
  <hr />
  <ApiHealth />

  <hr />
  <h2>Existing Tenant UI Components</h2>
  <Dashboard v-if="store.state.token" />
  <Login v-else />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}

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
