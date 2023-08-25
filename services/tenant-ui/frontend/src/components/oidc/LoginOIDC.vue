<template>
  <Button class="w-full mt-5" label="IDIR" :loading="loading" @click="login" />
  <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
  <div v-if="error">{{ $t('admin.error') }}: {{ error }}</div>
</template>

<script setup lang="ts">
import Button from 'primevue/button';
import { useOidcStore } from '@/store';

import { storeToRefs } from 'pinia';
import { useToast } from 'vue-toastification';

const toast = useToast();
const oidcStore = useOidcStore();
const { loading, error } = storeToRefs(useOidcStore());

// OIDC Login
const login = async () => {
  try {
    await oidcStore.login();
  } catch (error: any) {
    toast.error(`Failure: ${error}`);
  }
};
</script>
