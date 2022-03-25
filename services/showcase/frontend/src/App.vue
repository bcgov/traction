<template>
  <v-app>
    <BaseNotificationContainer />
    <AppHeader />
    <AppNavBar />

    <v-main>
      <transition name="component-fade" mode="out-in">
        <router-view />
      </transition>
    </v-main>

    <AppFooter />
  </v-app>
</template>

<script>
import AppHeader from '@/components/app/AppHeader.vue';
import AppFooter from '@/components/app/AppFooter.vue';
import AppNavBar from '@/components/app/AppNavBar.vue';

export default {
  name: 'App',
  components: {
    AppHeader,
    AppFooter,
    AppNavBar
  }
};
</script>

<style scoped>
.component-fade-enter-active,
.component-fade-leave-active {
  transition: opacity 0.3s ease;
}
.component-fade-enter,
.component-fade-leave-to {
  opacity: 0;
}
</style>
