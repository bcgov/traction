<template>
  <div class="card-content-container">
    <h3 class="mt-0">{{ props.title }}</h3>
    <slot />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string;
}>();
</script>

<style scoped lang="scss">
.card-content-container {
  margin-top: -35px;
}
</style>
