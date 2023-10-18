<template>
  <Message
    v-if="config.frontend.ux.infoBanner.showMessage"
    :severity="config.frontend.ux.infoBanner.messageLevel"
    :closable="false"
  >
    {{ config.frontend.ux.infoBanner.message }}
  </Message>
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
import Message from 'primevue/message';
const { config } = storeToRefs(useConfigStore());

console.log('config', config);
</script>
