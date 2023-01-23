<template>
  <h3 class="mt-0">{{ t('about.about') }}</h3>

  <Accordion :multiple="true">
    <AccordionTab
      v-if="
        config.frontend.ux.aboutBusiness &&
        config.frontend.ux.aboutBusiness.title
      "
      :header="config.frontend.ux.aboutBusiness.title"
    >
      <Business />
    </AccordionTab>
    <AccordionTab header="Traction">
      <Traction />
    </AccordionTab>
    <AccordionTab header="ACA-Py">
      <Acapy />
    </AccordionTab>
  </Accordion>
</template>

<script setup lang="ts">
// PrimeVue etc
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import { useI18n } from 'vue-i18n';
// State
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
// Components
import Acapy from '@/components/about/Acapy.vue';
import Business from '@/components/about/Business.vue';
import Traction from '@/components/about/Traction.vue';

const { t } = useI18n();
const { config } = storeToRefs(useConfigStore());
</script>
