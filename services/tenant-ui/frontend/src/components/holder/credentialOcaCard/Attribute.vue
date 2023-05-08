<template>
  <div class="text-container attribute-list">
    <span class="attribute-label">
      {{ displayAttributeLabel(props.attribute) }}
    </span>
    <span class="attribute-value">
      {{ displayAttributeValue(props.attribute) }}
    </span>
  </div>
</template>

<script setup lang="ts">
// Types
import OverlayBundle from '@/overlayLibrary/types/overlay/OverlayBundle';
import { OverlayAttribute } from '@/overlayLibrary/types/overlay/OverlayBundle';
import { IndyCredInfo } from '@/types/acapyApi/acapyInterface';

import { computed } from 'vue';
import { textColorForBackground } from '@/overlayLibrary/utils/color';

const props = defineProps<{
  attribute: string;
  credential?: IndyCredInfo;
  overlay?: OverlayBundle;
}>();

const displayAttributeLabel = (attributeName: string): string => {
  const attrLabel = props.overlay?.attributes.find(
    (attribute) => attribute.name === attributeName
  );
  return attrLabel?.label?.['en-CA'] ?? '';
};

const displayAttributeValue = (attributeName: string): any =>
  props.credential?.attrs?.[attributeName] ?? '';
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
