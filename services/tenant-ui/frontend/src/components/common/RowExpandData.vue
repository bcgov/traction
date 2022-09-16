<template>
  <div v-if="loading" class="flex justify-content-center">
    <ProgressSpinner />
  </div>
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
import { PropType } from 'vue';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import ProgressSpinner from 'primevue/progressspinner';
import VueJsonPretty from 'vue-json-pretty';

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
