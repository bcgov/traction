<template>
  <Button
    class="w-full mt-5"
    :label="config.frontend.oidc.label"
    :loading="loading"
    @click="oidcLogin"
  />
  <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
  <div v-if="error">{{ $t('admin.error') }}: {{ error }}</div>
</template>

<script setup lang="ts">
// State
import { useInnkeeperOidcStore } from '@/store';
import { storeToRefs } from 'pinia';
import { useConfigStore } from '../../store';
// PrimeVue/etc
import Button from 'primevue/button';
import { useToast } from 'vue-toastification';
const toast = useToast();

const { config } = storeToRefs(useConfigStore());

const innkeeperOidcStore = useInnkeeperOidcStore();
const { loading, error } = storeToRefs(useInnkeeperOidcStore());

// OIDC Login
const oidcLogin = async () => {
  try {
    await innkeeperOidcStore.login();
  } catch (error: any) {
    toast.error(`Failure: ${error}`);
  }
};
</script>
