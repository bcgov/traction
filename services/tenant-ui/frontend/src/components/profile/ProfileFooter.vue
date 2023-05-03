<template>
  <div class="grid">
    <div class="col-fixed w-8rem">
      <strong>{{ $t('profile.createdAt') }}</strong>
    </div>
    <div class="col">{{ formatDateLong(tenant.created_at) }}</div>
  </div>
  <div class="grid">
    <div class="col-fixed w-8rem">
      <strong>{{ $t('profile.updatedAt') }}</strong>
    </div>
    <div class="col">{{ formatDateLong(tenant.updated_at) }}</div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';
import { formatDateLong } from '@/helpers';

// tenant should be loaded by login...
const { tenant } = storeToRefs(useTenantStore());
</script>
