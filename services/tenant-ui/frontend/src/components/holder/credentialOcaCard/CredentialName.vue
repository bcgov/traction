<template>
  <div class="text-container">
    {{ displayName }}
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

const displayName = computed(() => {
  return props.overlay?.metadata?.name?.[
    localeDefault(props.overlay.metadata.name, locale.value as string)
  ];
});
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
