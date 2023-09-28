<template>
  <div class="parent">
    <Button class="p-button-rounded" @click="toggleProfile">
      <div class="wallet-img" />
    </Button>
    <div v-if="isIssuer" class="issuer-badge" />
  </div>
  <Menu ref="menu" :model="items" :popup="true" />
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Menu from 'primevue/menu';
// State
import { useConfigStore } from '@/store';
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const { config } = storeToRefs(useConfigStore());
const { isIssuer } = storeToRefs(useTenantStore());

const menu = ref();
const toggleProfile = (event: any) => {
  menu.value.toggle(event);
};

const items = [
  {
    label: t('common.profile'),
    to: { name: 'Profile' },
  },
  {
    label: t('common.settings'),
    to: { name: 'Settings' },
  },
  {
    label: t('apiKey.apiKeys'),
    to: { name: 'ApiKeys' },
  },
  {
    label: t('common.developer'),
    visible: config.value.frontend.showDeveloper,
    to: { name: 'Developer' },
  },
  {
    separator: true,
  },
  {
    label: t('common.logout'),
    class: 'logout-menu-item',
    url: '/logout',
  },
];
</script>

<style scoped lang="scss">
.parent {
  position: relative;
  top: 0;
  left: 0;
  button,
  button:hover {
    background-color: transparent !important;
  }
}
button {
  border: 0;
  border-radius: 50%;
  padding: 0;
  transition: all 0.2s ease-in-out;
}
.wallet-img {
  background-image: url('/img/badges/wallet.png');
  width: 45px;
  height: 45px;
  background-size: cover;
}
.issuer-badge {
  background-image: url('/img/badges/issuer_shield.png');
  width: 16px;
  height: 16px;
  position: absolute;
  bottom: -8px;
  left: 15px;
  background-size: cover;
}
button:enabled:hover {
  border: 0;
  transform: scale(1.1);
}
</style>
