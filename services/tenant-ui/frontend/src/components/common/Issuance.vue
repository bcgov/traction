<template>
  <Button
    :label="tenant.issuer ? 'Issuer' : 'Activate Issuer'"
    :icon="tenant.issuer ? 'pi pi-check' : 'pi pi-flag'"
    class="p-button"
    :disabled="tenant.issuer"
    :loading="loading"
  ></Button>
</template>

<script setup lang="ts">
import Button from 'primevue/button';
import { ref } from 'vue';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';

const loading = ref(false);

const { tenant } = storeToRefs(useTenantStore());
</script>
