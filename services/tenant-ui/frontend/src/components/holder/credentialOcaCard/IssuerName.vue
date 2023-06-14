<template>
  <div class="text-container">
    {{ issuerName }}
  </div>
</template>

<script setup lang="ts">
// Types
import OverlayBundle from '@/overlayLibrary/types/overlay/OverlayBundle';

// Overlay Library
import { textColorForBackground } from '@/overlayLibrary/utils/color';
import { localeDefault } from '@/overlayLibrary/utils/localeDefaults';
// i18n
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
const { locale } = useI18n({ useScope: 'global' });

const props = defineProps<{
  overlay?: OverlayBundle;
}>();

const issuerName = computed((): any => {
  return props.overlay?.metadata?.issuer?.[
    localeDefault(props.overlay.metadata.issuer, locale.value as string)
  ];
});
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
