<template>
  <div class="text-container">
    {{ overlay?.metadata?.name['en-CA'] }}
  </div>
</template>

<script setup lang="ts">
// Types
import OverlayBundle from '@/overlayLibrary/types/overlay/OverlayBundle';

import { textColorForBackground } from '@/overlayLibrary/utils/color';

const props = defineProps<{
  overlay?: OverlayBundle;
}>();
</script>

<style scoped>
.text-container {
  flex-shrink: 1;
  flex: 1;
  flex-wrap: wrap;
  color: v-bind(
    'textColorForBackground(overlay?.branding?.primaryBackgroundColor || "#000000")'
  );
  line-height: 24px;
  font-weight: bolder;
  font-size: 18px;
}
</style>
