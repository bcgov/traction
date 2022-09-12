<template>
  <Button @click="toggleProfile">
    <div class="wallet-img"></div>
  </Button>
  <Menu ref="menu" :model="items" :popup="true" />
</template>

<script setup lang="ts">
import Button from 'primevue/button';
import Menu from 'primevue/menu';
import { ref } from 'vue';

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
button {
  background-color: rgba(0, 0, 0, 0);
  border: 0;
  border-radius: 50%;
  padding: 0;
  transition: all 0.2s ease-in-out;
}
.wallet-img {
  background-image: url(/public/profile_003_64.png);
  width: 32px;
  height: 32px;
  background-size: cover;
  transition-duration: 2s;
}
button:enabled:hover {
  background-color: rgba(0, 0, 0, 0);
  border: 0;
  transform: scale(1.1);
}
</style>
