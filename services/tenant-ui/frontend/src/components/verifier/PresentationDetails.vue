<!-- Used to display presentation received after RFC-0037 Present-Proof-v1.0

 https://github.com/hyperledger/aries-rfcs/blob/main/features/0037-present-proof/README.md
 
 May work for RFC-0454 Present-Proof-v2.0, to be tested later.... and update this comment

 https://github.com/hyperledger/aries-rfcs/blob/main/features/0454-present-proof-v2/README.md
 -->

<template>
  <div v-if="presentation">
    <ul>
      <div v-if="props.header">
        <li>Status: {{ presentation.status }}</li>
        <li>Updated at: {{ formatDateLong(presentation.updated_at) }}</li>
        <li>Contact Alias: {{ presentation.contact.alias }}</li>
        <hr />
      </div>
      <!-- What does verified mean -->
      <div
        v-if="props.showInformation && presentation.status == 'verified'"
        class="information"
      >
        <span class="pi pi-check"></span
        ><span
          >Credential is held by
          <strong>{{ presentation.contact.alias }}</strong></span
        ><br />
        <span class="pi pi-check"></span><span>Credential is valid</span><br />
        <span class="pi pi-check"></span><span>Credential is tamper-free </span
        ><br />
        <span class="pi pi-check"></span
        ><span>All attribute restrictions were satisfied</span><br />
        <hr />
      </div>
      <VerifiedPresentationData
        v-if="presentation.status == 'verified'"
        :presentation="presentation"
      />
    </ul>
    <Accordion>
      <AccordionTab header="View Raw Content">
        <vue-json-pretty :data="presentation" />
      </AccordionTab>
    </Accordion>
  </div>
  <div v-else>...loading</div>
</template>

<script setup lang="ts">
import { PropType } from 'vue';
import { formatDateLong } from '@/helpers';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import VerifiedPresentationData from './VerifiedPresentationData.vue';

const props = defineProps({
  presentation: {
    type: Object as PropType<any>,
    required: true,
  },
  header: {
    type: Boolean as PropType<boolean>,
    required: false,
    default: true,
  },
  showInformation: {
    type: Boolean as PropType<boolean>,
    required: false,
    default: false,
  },
});
</script>

<style>
.presentation-attr-value {
  padding-left: 1em;
}

.information .pi.pi-check {
  font-size: 18px;
  color: green;
  margin-right: 5px;
}
</style>
