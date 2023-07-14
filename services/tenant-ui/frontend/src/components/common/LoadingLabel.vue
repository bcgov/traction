<template>
  <div class="loading-label">
    <div v-if="value !== undefined">{{ value }}</div>
    <div v-else>
      <ProgressSpinner :style="progressStyle" aria-label="Loading" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { PropType, ref } from 'vue';
import ProgressSpinner from 'primevue/progressspinner';

const props = defineProps({
  value: {
    type: String as PropType<string | undefined>,
  },
  size: {
    type: Number as PropType<number>,
    default: 1,
  },
});

const progressStyle = ref({
  width: `${props.size}rem`,
  height: `${props.size}rem`,
});
</script>
