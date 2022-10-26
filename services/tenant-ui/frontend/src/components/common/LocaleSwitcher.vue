<template>
  <Dropdown v-model="locale" :options="localeList" class="mr-4" />
</template>

<script setup lang="ts">
import Dropdown from 'primevue/dropdown';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n({ useScope: 'global' });

const localeList = ['en', 'fr', 'jp'];
</script>

<style lang="scss" scoped>
.p-dropdown {
  :deep(.p-dropdown-label) {
    padding: 0 0 0 6px !important;
  }
}
</style>
