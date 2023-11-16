<template>
  <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
  <h2>{{ $t('profile.config') }}</h2>
  <vue-json-pretty :data="config" />
  <JWT />
</template>

<script setup lang="ts">
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store';
import JWT from './JWT.vue';
import 'primeicons/primeicons.css';

// tenant should be loaded by login...
const { config } = storeToRefs(useConfigStore());
</script>
