<template>
  <div class="container">
    <div class="card-container">
      <CardSecondaryBody :branding="props.overlay?.branding" />
      <CardLogo :branding="props.overlay?.branding" />
      <CardPrimaryBody :overlay="overlay" :credential="props.credential" />
      <!-- <CardStatus overlay="{overlay}" styles="{styles}" />  -->
    </div>
  </div>
</template>

<script setup lang="ts">
// Types
import OverlayBundle from '@/overlayLibrary/types/overlay/OverlayBundle';
import { IndyCredInfo } from '@/types/acapyApi/acapyInterface';

import { computed } from 'vue';
import { DIMENSIONS as D } from './OcaStyleConstants';
import CardPrimaryBody from './CardPrimaryBody.vue';
import CardSecondaryBody from './CardSecondaryBody.vue';
import CardLogo from './CardLogo.vue';

const props = defineProps<{
  overlay?: OverlayBundle;
  credential: IndyCredInfo;
}>();
const branding = computed(() => props.overlay?.branding);
</script>

<style scoped>
.container {
  width: 360px;
  background-color: v-bind(
    'branding?.primaryBackgroundColor || "rgba(0, 0, 0, 0.24)"'
  );
  border-radius: v-bind('D.borderRadius + "px"');
}

.card-container {
  display: flex;
  flex-direction: row;
  min-height: v-bind('(D.width * .33) + "px"');
}
</style>
