<template>
  <Button
    icon="pi pi-wallet"
    class="p-button-icon p-button-rounded"
    @click="toggleProfile"
  />
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
    command: () => {
      console.log('profile');
    },
  },
  {
    label: 'Settings',
    icon: 'pi pi-cog',
    command: () => {
      console.log('settings');
    },
  },
  {
    label: 'Logout',
    icon: 'pi pi-sign-out',
    command: () => {
      console.log('logout');
    },
  },
];
</script>
<style scoped></style>
