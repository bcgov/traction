<template>
  <div class="text-container">
    {{ issuerName }}
  </div>
</template>

<script setup lang="ts">
// Types
import OverlayBundle from '@/overlayLibrary/types/overlay/OverlayBundle';

import { computed } from 'vue';
import { textColorForBackground } from '@/overlayLibrary/utils/color';

const props = defineProps<{
  overlay?: OverlayBundle;
}>();

const issuerName = computed(
  () => props.overlay?.metadata?.issuer?.['en-CA'] ?? ''
);
</script>

<style scoped>
.text-container {
  display: flex;
  flex-shrink: 1;
  flex-wrap: wrap;
  color: v-bind(
    'textColorForBackground(overlay?.branding?.primaryBackgroundColor || "#000000")'
  );
  line-height: 19px;
  opacity: 0.8;
  font-weight: bold;
  font-size: 14px;
}
</style>
