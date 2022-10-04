<template>
  <AppLayout v-if="tenantReady" />
  <Login v-else />
</template>

<script setup lang="ts">
import AppLayout from '@/components/layout/AppLayout.vue';
import Login from '@/components/Login.vue';
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';

const { tenantReady } = storeToRefs(useTenantStore());
</script>
