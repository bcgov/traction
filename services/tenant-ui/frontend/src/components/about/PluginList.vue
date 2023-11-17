<template>
  <Accordion>
    <AccordionTab :header="$t('about.acaPy.plugins')">
      <div v-if="loading" class="flex justify-content-center">
        <ProgressSpinner />
      </div>
      <vue-json-pretty v-else :data="acapyPlugins" />
    </AccordionTab>
  </Accordion>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
// PrimeVue
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import ProgressSpinner from 'primevue/progressspinner';
import VueJsonPretty from 'vue-json-pretty';

const { acapyPlugins, loading } = storeToRefs(useConfigStore());
const configStore = useConfigStore();

configStore.getPluginList();
</script>

<style scoped>
.logo-acapy {
  width: 14em;
}
</style>
