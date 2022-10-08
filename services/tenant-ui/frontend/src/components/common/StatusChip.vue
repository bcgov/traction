<template>
  <Chip :class="statusClass">
    <span class="text">{{ status }}</span>
  </Chip>
</template>

<script setup lang="ts">
import { toKebabCase } from '@/helpers';
import Chip from 'primevue/chip';
import { computed } from 'vue';
const props = defineProps({
  status: {
    type: String,
    required: true,
  },
  class: {
    type: String,
    required: false,
    default() {
      return '';
    },
  },
});

const statusClass = computed(() => {
  const classes = ['status-chip'];
  // add a specific class for this status to get colours
  classes.push(toKebabCase(props.status));
  // if we have specified an additional class pass that in...
  classes.push(props.class);
  return classes;
});
</script>
