<template>
  <div class="secondary-body-container">
    <img
      v-if="props.branding?.backgroundImageSlice"
      :src="props.branding.backgroundImageSlice"
    />
  </div>
</template>

<script setup lang="ts">
// Types
import { BrandingOverlay } from '@/overlayLibrary/types/overlay/BrandingOverlay';

import { DIMENSIONS as D } from './OcaStyleConstants';

const props = defineProps<{
  branding?: BrandingOverlay;
}>();
</script>

<style scoped>
.secondary-body-container {
  flex-shrink: 0;
  width: v-bind('D.logoHeight + "px"');
  border-top-left-radius: v-bind('D.borderRadius + "px"');
  border-bottom-left-radius: v-bind('D.borderRadius + "px"');
  background-color: v-bind(
    '(branding?.backgroundImageSlice ? "rgba(0, 0, 0, 0)" : branding?.secondaryBackgroundColor) || "rgba(0, 0, 0, 0.24)"'
  );
}

.card-container {
  flex-direction: row;
  min-height: v-bind('(D.width * .33) + "px"');
}

.secondary-body-container img {
}
</style>
