<template>
  <Message
    v-if="stringOrBooleanTruthy(config.frontend.ux.infoBanner?.showMessage)"
    :severity="config.frontend.ux.infoBanner.messageLevel"
    :closable="false"
  >
    {{ config.frontend.ux.infoBanner.message }}
  </Message>
</template>
<script setup lang="ts">
import Message from 'primevue/message';
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
const { config } = storeToRefs(useConfigStore());
import { stringOrBooleanTruthy } from '@/helpers';
</script>
