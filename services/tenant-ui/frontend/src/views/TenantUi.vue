<template>
  <div class="alert-container">
    <Alert class="z-2" />
    <AppLayout v-if="tenantReady" />
    <Login v-else />
  </div>
</template>

<script setup lang="ts">
import Alert from '@/components/notifications/Alert.vue';
import AppLayout from '@/components/layout/AppLayout.vue';
import Login from '@/components/Login.vue';
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';

const { tenantReady } = storeToRefs(useTenantStore());
</script>

<style scoped lang="scss">
// This is the info banner alert that is shown on all pages
.p-message {
  margin: 0;
  border-radius: 0;
}
</style>
