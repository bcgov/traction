<template>
  <div class="loading-label">
    <div v-if="value !== undefined">{{ value }}</div>
    <div v-else>
      <ProgressSpinner :style="progressStyle" aria-label="Loading" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ProgressSpinner from 'primevue/progressspinner';

const props = withDefaults(
  defineProps<{
    value?: string;
    size?: number;
  }>(),
  {
    value: undefined,
    size: 1,
  }
);

const progressStyle = ref({
  width: `${props.size}rem`,
  height: `${props.size}rem`,
});
</script>
