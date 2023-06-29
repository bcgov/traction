<template>
  <div class="card-content-container">
    <div class="flex justify-content-between">
      <h3 class="mt-0">{{ props.title }}</h3>
      <div class="flex justify-content-end card-right-buttons">
        <slot name="buttons" />

        <Button
          v-if="props.refreshCallback"
          icon="pi pi-refresh"
          :title="$t('common.refreshTable')"
          text
          rounded
          @click="props.refreshCallback"
        />
      </div>
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
import Button from 'primevue/button';
const props = defineProps<{
  title: string;
  refreshCallback?: () => void;
}>();
</script>

<style scoped lang="scss">
.card-content-container {
  margin-top: -35px;
}
.card-right-buttons {
  margin-top: -0.5rem;
  margin-right: 3rem;
}
</style>
