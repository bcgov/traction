<template>
  <Card :class="{ cardExpanded: cardExpanded }">
    <template #content>
      <div class="flex justify-content-end">
        <ExpandButton />
      </div>
      <slot />
    </template>
  </Card>
</template>

<script setup lang="ts">
// View
import Card from 'primevue/card';
import ExpandButton from './ExpandButton.vue';
//State
import { useCommonStore } from '@/store/commonStore';
import { storeToRefs } from 'pinia';
const { cardExpanded } = storeToRefs(useCommonStore());
</script>

<style scoped lang="scss">
.cardExpanded {
  position: fixed;
  top: 10px;
  left: 10px;
  height: calc(100% - 20px);
  width: calc(100% - 20px);
  overflow: auto;
  z-index: 3;

  border: 1px solid lightgray;
}
</style>
