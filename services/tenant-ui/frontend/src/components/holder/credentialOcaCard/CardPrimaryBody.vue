<template>
  <div class="primary-body-container">
    <IssuerName :overlay="props.overlay" />
    <!-- <CredentialName
      overlay="{overlay}"
      language="{language}"
      styles="{styles}"
    />
    {displayAttributes.map((attribute, index) => (
    <Attribute
      key="{`${attribute}_${index}}`}"
      overlay="{overlay}"
      language="{language}"
      attribute="{attribute}"
      styles="{styles}"
    />
    ))} -->
  </div>
</template>

<script setup lang="ts">
// Types
import OverlayBundle from '@/overlayLibrary/types/overlay/OverlayBundle';

import IssuerName from './IssuerName.vue';
import { DIMENSIONS as D } from './OcaStyleConstants';

const props = defineProps<{
  overlay?: OverlayBundle;
}>();
</script>

<style scoped>
.primary-body-container {
  display: flex;
  flex-direction: column;
  flex-basis: auto;
  padding: v-bind('D.padding + "px"');
  flex-shrink: 1;
}
</style>
