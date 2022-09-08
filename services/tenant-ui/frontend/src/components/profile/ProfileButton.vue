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
<style scoped></style>
