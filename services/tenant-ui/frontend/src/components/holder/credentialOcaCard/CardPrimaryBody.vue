<template>
  <div class="primary-body-container">
    <div v-if="overlay">
      <IssuerName :overlay="props.overlay" />
      <CredentialName :overlay="props.overlay" />
      <div v-if="attributes" class="flex flex-column">
        <Attribute
          v-for="(attr, index) in displayAttributes"
          :key="index"
          :attribute="attr"
          :credential="credential"
          :overlay="props.overlay"
          class="mt-3"
        />
      </div>
    </div>
    <div v-else>
      <i class="pi pi-exclamation-triangle"></i>
      {{ $t('credentials.wallet.noOca') }} <br />
      {{ $t('credentials.wallet.noOcaNotImpl') }}
    </div>
  </div>
</template>

<script setup lang="ts">
// Types
import OverlayBundle from '@/overlayLibrary/types/overlay/OverlayBundle';
import { IndyCredInfo } from '@/types/acapyApi/acapyInterface';

import Attribute from './Attribute.vue';
import CredentialName from './CredentialName.vue';
import IssuerName from './IssuerName.vue';
import { DIMENSIONS as D } from './OcaStyleConstants';
import { computed } from 'vue';

const props = defineProps<{
  overlay?: OverlayBundle;
  credential?: IndyCredInfo;
}>();

const attributes = computed(
  (): Record<string, string> | never[] => props.credential?.attrs || []
);

const displayAttributes: string[] = [];
const { primaryAttribute, secondaryAttribute } = props.overlay?.branding ?? {};
if (primaryAttribute) {
  displayAttributes.push(primaryAttribute);
}
if (secondaryAttribute) {
  displayAttributes.push(secondaryAttribute);
}
</script>

<style scoped>
.primary-body-container {
  display: flex;
  flex-direction: column;
  flex-basis: auto;
  padding: v-bind('D.padding + "px"');
  padding-left: 0;
  flex-shrink: 1;
}
</style>
