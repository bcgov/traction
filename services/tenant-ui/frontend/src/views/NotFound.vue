<template>
  <div class="text-center">
    <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
    <h1>{{ $t('httpStatus.404.code') }}: {{ $t('httpStatus.404.status') }}</h1>
    <router-link :to="{ name: 'Dashboard' }">
      <Button :label="$t('dashboard.backToDashboard')" class="p-button-link" />
    </router-link>
  </div>
</template>

<script setup lang="ts">
import Button from 'primevue/button';
</script>
