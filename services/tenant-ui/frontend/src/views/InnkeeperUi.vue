<template>
  <InnkeeperLayout v-if="innkeeperReady" />
  <InnkeeperLogin v-else />
</template>

<script setup lang="ts">
import InnkeeperLayout from '@/components/layout/innkeeper/InnkeeperLayout.vue';
import InnkeeperLogin from '@/components/innkeeper/InnkeeperLogin.vue';
import { storeToRefs } from 'pinia';
import { useInnkeeperTokenStore } from '@/store';

const { innkeeperReady } = storeToRefs(useInnkeeperTokenStore());
</script>
