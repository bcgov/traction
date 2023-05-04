<template>
  <div class="text-container attribute-list">
    <span class="attribute-label">
      {{ displayAttributeLabel(props.attribute).label['en-CA'] }}
    </span>
    <span class="attribute-value">
      {{ displayAttributeValue(props.attribute)?.value }}
    </span>
  </div>
</template>

<script setup lang="ts">
// Types
import OverlayBundle from '@/overlayLibrary/types/overlay/OverlayBundle';
import { OverlayAttribute } from '@/overlayLibrary/types/overlay/OverlayBundle';
import {
  CredAttrSpec,
  V10CredentialExchange,
} from '@/types/acapyApi/acapyInterface';

import { textColorForBackground } from '@/overlayLibrary/utils/color';

const props = defineProps<{
  attribute: string;
  credential?: V10CredentialExchange;
  overlay?: OverlayBundle;
}>();

const displayAttributeLabel = (
  attributeName: string
): OverlayAttribute | undefined => {
  return props.overlay?.attributes.find(
    (attribute) => attribute.name === attributeName
  );
};

const displayAttributeValue = (
  attributeName: string
): CredAttrSpec | undefined => {
  return props.credential?.credential_offer_dict?.credential_preview?.attributes.find(
    (attribute) => attribute.name === attributeName
  );
};
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
