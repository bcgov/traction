<template>
  <div class="parent">
    <Button @click="toggleProfile">
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
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
const { isIssuer } = storeToRefs(useTenantStore());

const menu = ref();
/**
 * Toggle the profile menu
 */
const toggleProfile = (event: any) => {
  menu.value.toggle(event);
};

const items = [
  {
    label: 'Profile',
    icon: 'pi pi-user',
    to: { name: 'Profile' },
  },
  {
    label: 'Settings',
    icon: 'pi pi-cog',
    to: { name: 'Settings' },
  },
  {
    label: 'Logout',
    icon: 'pi pi-sign-out',
    url: '/', // TODO: this should be a logout route
  },
];
</script>

<style scoped>
.parent {
  position: relative;
  top: 0;
  left: 0;
}
button {
  background-color: rgba(0, 0, 0, 0);
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
  bottom: -6px;
  left: 15px;
  background-size: cover;
}
button:enabled:hover {
  background-color: rgba(0, 0, 0, 0);
  border: 0;
  transform: scale(1.1);
}
</style>
