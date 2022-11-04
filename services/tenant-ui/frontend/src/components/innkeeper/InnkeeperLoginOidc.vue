<template>
  {{ config }}
  <Button @click="oidcLogin" class="w-full mt-5" label="IDIR" />

  {{ user }}
</template>

<script setup lang="ts">
//Vue
import { ref, reactive } from 'vue';
// State
import { useConfigStore } from '@/store';
import { useInnkeeperOidcStore } from '@/store';
import { storeToRefs } from 'pinia';
// PrimeVue/Validation/etc
import Button from 'primevue/button';

const { config } = storeToRefs(useConfigStore());
const innkeeperOidcStore = useInnkeeperOidcStore();
const { user } = storeToRefs(useInnkeeperOidcStore());

// OIDC Login
const oidcLogin = () => {
  innkeeperOidcStore.login();
};
</script>
