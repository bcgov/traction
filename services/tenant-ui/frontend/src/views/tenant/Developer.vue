<template>
  <h3 class="mt-0">{{ $t('tenant.developer.tenantDeveloper') }}</h3>

  <Developer />
</template>

<script setup lang="ts">
import Developer from '@/components/profile/Developer.vue';
</script>
