<template>
  <div class="grid align-items-start">
    <div class="col-12 md:col-6">
      <strong>{{ t('about.acaPy.info') }}</strong>
      <p class="mt-0">
        {{
          t('about.acaPy.acapyVersion', {
            version: config.frontend.ariesDetails.acapyVersion,
          })
        }}
      </p>
    </div>
    <div class="col-12 md:col-6 flex justify-content-end pt-0">
      <img src="/img/logo/aries-logo-color.png" class="logo-acapy" />
    </div>
  </div>

  <div class="grid">
    <div class="col-2">
      {{ t('about.acaPy.ledger') }}
    </div>
    <div class="col-10">
      {{ config.frontend.ariesDetails.ledgerName }}
    </div>

    <div class="col-2">
      {{ t('about.acaPy.ledgerBrowser') }}
    </div>
    <div class="col-10">
      {{ config.frontend.ariesDetails.ledgerBrowser }}
    </div>

    <div class="col-2">
      {{ t('about.acaPy.tailsServer') }}
    </div>
    <div class="col-10">
      {{ config.frontend.ariesDetails.tailsServer }}
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
.logo-acapy {
  width: 14em;
}
</style>
