<template>
  <router-link
    v-if="props.item.route"
    v-slot="{ href, navigate }"
    :to="props.item.route"
    custom
  >
    <a :href="href" class="p-panelmenu-header-action" @click="navigate">
      <span class="p-menuitem-icon" :class="props.item.icon" />
      <span class="p-menuitem-text ml-2 text-color">{{
        props.item.label
      }}</span>
    </a>
  </router-link>
  <a
    v-else
    :href="props.item.url"
    class="p-panelmenu-header-action"
    :target="props.item.target"
  >
    <span class="p-menuitem-icon" :class="props.item.icon" />
    <span class="p-menuitem-text ml-2">{{ props.item.label }}</span>
    <span
      v-if="props.item.items"
      class="pi pi-angle-down text-primary ml-auto"
    />
  </a>
</template>

<script setup lang="ts">
// See https://primevue.org/panelmenu/#router
import type { MenuItem } from 'primevue/menuitem';

const props = defineProps<{
  item: MenuItem;
}>();
</script>

<style scoped></style>
