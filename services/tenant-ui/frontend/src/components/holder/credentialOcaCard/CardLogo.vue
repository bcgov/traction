<template>
  <div class="logo-container">
    <img v-if="props.branding?.logo" :src="props.branding.logo" />
    <div v-else class="logo-text"></div>
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
.logo-container {
  display: flex;
  flex-shrink: 0;
  position: relative;
  top: v-bind('D.padding + "px"');
  left: v-bind('(-1 * D.logoHeight + D.padding) + "px"');
  width: v-bind('D.logoHeight + "px"');
  height: v-bind('D.logoHeight + "px"');
  background-color: rgba(255, 255, 255, 1);
  border-radius: 8px;
  justify-content: center;
  align-items: center;
}

.logo-container img {
  width: v-bind('D.logoHeight + "px"');
  height: v-bind('D.logoHeight + "px"');
  border-radius: 8px;
}

.logo-text {
  font-size: v-bind('(0.5* D.logoHeight) + "px"');
  font-weight: bold;
  align-self: center;
}
</style>
