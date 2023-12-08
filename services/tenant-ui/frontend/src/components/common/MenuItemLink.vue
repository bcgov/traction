<template>
  <router-link
    v-if="item.route"
    v-slot="{ href, navigate }"
    :to="item.route"
    custom
  >
    <a v-ripple :href="href" v-bind="menuBindProps.action" @click="navigate">
      <span :class="item.icon" />
      <span class="ml-2">{{ item.label }}</span>
    </a>
  </router-link>
  <a
    v-else
    v-ripple
    :href="item.url"
    :target="item.target"
    v-bind="menuBindProps.action"
  >
    <span :class="item.icon" />
    <span class="ml-2">{{ item.label }}</span>
  </a>
</template>

<script setup lang="ts">
import type { MenuItem } from 'primevue/menuitem';
import type { MenuRouterBindProps } from 'primevue/menu';

defineProps<{
  item: MenuItem;
  menuBindProps: MenuRouterBindProps;
}>();
</script>

<style scoped></style>
