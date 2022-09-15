<template>
  <div v-if="loading">Loading data. Please wait...</div>
  <div v-else>
    <div>
      <slot name="details" v-bind="data"></slot>
    </div>
    <Accordion>
      <AccordionTab header="View Raw Content">
        <vue-json-pretty :data="data" />
      </AccordionTab>
    </Accordion>
  </div>
</template>

<script setup lang="ts">
import { computed, PropType, ref } from 'vue';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import { JSONDataType } from 'vue-json-pretty/types/utils';
import { processSlotOutlet } from '@vue/compiler-core';

const props = defineProps({
  data: {
    type: null as unknown as PropType<any>,
    required: true,
  },
  loading: {
    type: Boolean,
  },
});
</script>
