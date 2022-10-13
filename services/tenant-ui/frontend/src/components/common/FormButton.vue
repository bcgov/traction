<!---------------------------------------------------------------
  Standardized form button
-->
<template>
  <div>
    <Button
      :label="label"
      :icon="icon"
      :class="calcClass()"
      :disabled="disabled"
      :loading="loading"
      @click="submit()"
    ></Button>
  </div>
</template>
<script setup lang="ts">
import Button from 'primevue/button';

const props = defineProps({
  icon: {
    // All buttons should have icons
    type: String,
    required: true,
  },
  submit: {
    // What's a button within logic
    type: Function,
    required: true,
  },
  label: {
    // If no label, use the icon
    type: String,
    required: false,
    default: '',
  },
  disabled: {
    // If disabled, don't submit
    type: Boolean,
    required: false,
    default: false,
  },
  loading: {
    // If loading, don't submit
    type: Boolean,
    required: false,
    default: false,
  },
});

const calcClass = () => {
  return props.label ? 'p-button' : 'p-button-rounded p-button-outlined';
};
</script>
<style scoped></style>
