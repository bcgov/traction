<template>
  <div v-if="loading" class="flex justify-content-center">
    <ProgressSpinner />
  </div>

  <div v-if="item">
    <div>
      <slot name="details" v-bind="item"></slot>
    </div>
    <Accordion>
      <AccordionTab :header="label">
        <vue-json-pretty :data="item" />
      </AccordionTab>
    </Accordion>
  </div>

  <div v-if="error">
    <Accordion>
      <AccordionTab>
        <template #header>
          <i class="pi pi-exclamation-circle mr-2 error-text"></i>
          <span class="error-text">
            {{
              $t('common.errorGettingUrl', {
                url: url,
              })
            }}
          </span>
        </template>
        <p>{{ error }}</p>
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
  id: {
    type: String,
    default: undefined,
  },
  label: {
    type: String,
    default: 'View Raw Content',
  },
  params: {
    type: Object,
    required: false,
    default() {
      return {};
    },
  },
  url: {
    type: String,
    required: true,
  },
});

const { error, loading, item, fetchItem } = useGetItem(props.url);

// ok, let's load up the row with acapy data...
fetchItem(props.id, props.params);
</script>

<style>
.error-text {
  color: red;
}
</style>
