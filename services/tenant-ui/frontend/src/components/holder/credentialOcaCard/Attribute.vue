<template>
  <div class="text-container attribute-list">
    <span class="attribute-label">
      {{ displayAttributeLabel }}
    </span>
    <span class="attribute-value">
      {{ displayAttributeValue() }}
    </span>
  </div>
</template>

<script setup lang="ts">
// Types
import OverlayBundle from '@/overlayLibrary/types/overlay/OverlayBundle';
import { IndyCredInfo } from '@/types/acapyApi/acapyInterface';

// Overlay Library
import { textColorForBackground } from '@/overlayLibrary/utils/color';
import { localeDefault } from '@/overlayLibrary/utils/localeDefaults';

// Other Imports
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
const { locale } = useI18n({ useScope: 'global' });

const props = defineProps<{
  attribute: string;
  credential?: IndyCredInfo;
  overlay?: OverlayBundle;
}>();

const displayAttributeLabel = computed(() => {
  const attrLabel = props.overlay?.attributes.find(
    (attribute) => attribute.name === props.attribute
  );
  return (
    attrLabel?.label?.[
      localeDefault(attrLabel.label, locale.value as string)
    ] ?? ''
  );
});

const displayAttributeValue = (): any =>
  props.credential?.attrs?.[props.attribute] ?? '';
</script>

<style scoped>
.attribute-list {
  flex-direction: column;
}
.text-container {
  display: flex;
  flex-shrink: 1;
  flex-wrap: wrap;
  color: v-bind(
    'textColorForBackground(overlay?.branding?.primaryBackgroundColor || "#000000")'
  );
  line-height: 19px;
  font-weight: normal;
  font-size: 14px;
}
.attribute-label {
  opacity: 0.8;
}
.attribute-value {
  color: v-bind(
    'textColorForBackground(overlay?.branding?.primaryBackgroundColor || "#000000")'
  );
  font-weight: bolder;
}
</style>
