<template>
  <Dropdown v-model="locale" :options="localeList" class="mr-4" />
</template>

<script setup lang="ts">
import Dropdown from 'primevue/dropdown';
import { useI18n } from 'vue-i18n';
import { i18nLocale } from '@/helpers';

const { locale } = useI18n({ useScope: 'global' });

const localeList: Array<i18nLocale> = ['en', 'fr', 'jp'];
</script>

<style lang="scss" scoped>
.p-dropdown {
  border: none;
  padding: 0 1.5em;
  :deep(.p-dropdown-trigger) {
    display: none;
  }
  :deep(.p-dropdown-label) {
    color: $tenant-ui-link-color;
  }
}
</style>
