<template>
  <div class="grid">
    <div class="col-3">{{ config.frontend.ux.aboutBusiness.linkTitle }}</div>
    <div class="col-9 md:col-6">
      <a :href="config.frontend.ux.aboutBusiness.link">{{
        config.frontend.ux.aboutBusiness.link
      }}</a>
    </div>
    <div
      v-if="config.frontend.ux.aboutBusiness.imageUrl"
      class="col-12 md:col-3 flex justify-content-end pt-0"
    >
      <img
        :src="config.frontend.ux.aboutBusiness.imageUrl"
        class="logo-business"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
const { config } = storeToRefs(useConfigStore());
</script>

<style scoped>
.logo-business {
  width: 18em;
}
</style>
