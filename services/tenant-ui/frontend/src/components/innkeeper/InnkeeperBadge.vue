<template>
  <div class="parent">
    <Button class="p-button-rounded" @click="toggleProfile">
      <div class="badge-img" />
    </Button>
  </div>
  <Menu ref="menu" :model="items" :popup="true">
    <template #item="{ item, props }">
      <MenuItemLink :item="item" :menu-bind-props="props" />
    </template>
  </Menu>
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Menu from 'primevue/menu';
// Components
import MenuItemLink from '@/components/common/MenuItemLink.vue';

const menu = ref();
/**
 * Toggle the profile menu
 */
const toggleProfile = (event: any) => {
  menu.value.toggle(event);
};

const items = [
  {
    label: 'Logout',
    class: 'logout-menu-item',
    url: '/innkeeper/logout',
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
.badge-img {
  background-image: url('/img/innkeeper/innkeeper-badge.png');
  width: 45px;
  height: 45px;
  background-size: cover;
}
button:enabled:hover {
  background-color: rgba(0, 0, 0, 0);
  border: 0;
  transform: scale(1.1);
}
</style>
