<script setup lang="ts">
import AppLayout from "./components/layout/AppLayout.vue";
import Login from "./components/Login.vue";
import {onMounted} from "vue";
import {storeToRefs} from "pinia";
import {useConfigStore} from "./store/configStore";
import {useTokenStore} from "./store/tokenStore";

const { config } = storeToRefs(useConfigStore());
const { token } = storeToRefs(useTokenStore());

onMounted(()=> {
  document.title = config.value.ux.appTitle;
});
</script>

<template>
  <AppLayout v-if="token" />
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
