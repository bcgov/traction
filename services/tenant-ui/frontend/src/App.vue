<script setup lang="ts">
import AppLayout from "./components/layout/AppLayout.vue";
import Login from "./components/Login.vue";
import store from "./store";
import {inject, onMounted, provide} from "vue";


const config: any = inject("config");

provide("store", store); // Allow the entire app to see the store.

onMounted(()=> {
  document.title = config.ux.appTitle;
})
</script>

<template>
  <AppLayout v-if="store.state.token" />
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
