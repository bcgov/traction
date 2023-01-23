<template>
  <div class="grid align-items-start">
    <div class="col-12 md:col-6">
      <strong>{{ t('about.traction.info') }}</strong>
      <p class="my-0">
        {{ t('about.traction.tractionVersion', { version: '0.2.2' }) }}
      </p>
      <p class="mt-0">
        {{ t('about.traction.uiVersion', { version: '0.2.2' }) }}
      </p>
    </div>

    <div class="col-12 md:col-6 flex justify-content-end pt-0">
      <img src="/img/logo/traction-logo-bc-text.svg" class="logo-trac" />
    </div>
  </div>

  <div class="grid">
    <div class="col-2">
      {{ t('about.traction.url') }}
    </div>
    <div class="col-10">
      {{ config.frontend.tenantProxyPath }}
    </div>

    <div class="col-2">
      {{ t('about.traction.imageTag') }}
    </div>
    <div class="col-10">
      {{ config.image.tag }}
    </div>

    <div class="col-2">
      {{ t('about.traction.imageVersion') }}
    </div>
    <div class="col-10">
      {{ config.image.version }}
    </div>

    <div class="col-2">
      {{ t('about.traction.imageCreated') }}
    </div>
    <div class="col-10">
      {{ config.image.buildtime }}
    </div>

    <div class="col-2">
      {{ t('about.traction.repository') }}
    </div>
    <div class="col-10">
      <a href="https://github.com/bcgov/traction">
        https://github.com/bcgov/traction
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const { config } = storeToRefs(useConfigStore());
</script>

<style scoped>
.logo-trac {
  width: 25em;
}
</style>
