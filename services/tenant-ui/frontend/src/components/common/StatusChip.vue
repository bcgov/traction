<template>
  <Chip :class="statusClass">{{ status }}</Chip>
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
});

const statusClass = computed(() => {
  const classes = ['status-chip'];
  // add a specific class for this status to get colours
  classes.push(toKebabCase(props.status));
  return classes;
});
</script>
