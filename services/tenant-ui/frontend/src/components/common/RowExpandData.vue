<template>
  <div v-if="loading" class="flex justify-content-center">
    <ProgressSpinner />
  </div>
  <div v-if="item">
    <div>
      <slot name="details" v-bind="item"></slot>
    </div>
    <Accordion>
      <AccordionTab header="View Raw Content">
        <vue-json-pretty :data="item" />
      </AccordionTab>
    </Accordion>
  </div>
</template>

<script async setup lang="ts">
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import ProgressSpinner from 'primevue/progressspinner';
import VueJsonPretty from 'vue-json-pretty';
import useGetItem from '@/composables/useGetItem';

const props = defineProps({
  url: {
    type: String,
    required: true,
  },
  id: {
    type: String,
    required: true,
  },
  params: {
    type: Object,
    required: false,
    default() {
      return {};
    },
  },
});

const { loading, item, fetchItem } = useGetItem(props.url);

// ok, let's load up the row with acapy data...
fetchItem(props.id, props.params);
</script>
