<!---------------------------------------------------------------
  Standardized form submission button
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
    type: String,
    required: true,
  },
  submit: {
    type: Function,
    required: true,
  },
  label: {
    type: String,
    required: false,
  },
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  },
  loading: {
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
