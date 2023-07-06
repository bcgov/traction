<template>
  <MainCardContent :title="$t('about.about')">
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
  </MainCardContent>
</template>

<script setup lang="ts">
// PrimeVue etc
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
// State
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store/configStore';
// Components
import Acapy from '@/components/about/Acapy.vue';
import Business from '@/components/about/Business.vue';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import Traction from '@/components/about/Traction.vue';

const { config } = storeToRefs(useConfigStore());
</script>
