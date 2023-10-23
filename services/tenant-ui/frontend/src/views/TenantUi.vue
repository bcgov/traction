<template>
  <Alert v-if="tenantReady" />
  <AppLayout v-if="tenantReady" />
  <Login v-else />
</template>

<script setup lang="ts">
import AppLayout from '@/components/layout/AppLayout.vue';
import Login from '@/components/Login.vue';
import Alert from '@/components/notifications/Alert.vue';
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';

const { tenantReady } = storeToRefs(useTenantStore());
</script>

<style scoped lang="scss">
/* This is a header notificaiton that is shown on all pages */
.notification,
.p-message {
  margin: 0;
  border-radius: 0;
}
</style>
