<template>
  <div class="alert-container">
    <Alert class="z-2" />
    <InnkeeperLayout v-if="innkeeperReady" />
    <InnkeeperLogin v-else />
  </div>
</template>

<script setup lang="ts">
import Alert from '@/components/notifications/Alert.vue';
import InnkeeperLayout from '@/components/layout/innkeeper/InnkeeperLayout.vue';
import InnkeeperLogin from '@/components/innkeeper/InnkeeperLogin.vue';
import { storeToRefs } from 'pinia';
import { useInnkeeperTokenStore } from '@/store';

const { innkeeperReady } = storeToRefs(useInnkeeperTokenStore());
</script>

<style scoped lang="scss">
.p-message {
  margin: 0;
  border-radius: 0;
}
</style>
