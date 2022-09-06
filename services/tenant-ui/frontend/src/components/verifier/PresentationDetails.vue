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

      <!-- VERIFIED Meaning-->
      <div v-if="props.showInformation && presentation.status == 'verified'">
        <span class="pi pi-check"></span
        ><span
          >Credential is held by
          <strong>{{ presentation.contact.alias }}</strong></span
        ><br />
        <span class="pi pi-check"></span><span>Credential is valid</span><br />
        <span class="pi pi-check"></span><span>Credential is tamper-free </span
        ><br />
        <span class="pi pi-check"></span
        ><span>All attribute restrictions were statisfied</span><br />
      </div>
      <hr />
      <!-- PRESENTATION RECEIVED-->
      <!-- requested_attributes using 'names' list -> revealed attribute groups -->
      <div v-if="presentation.acapy.presentation_exchange.presentation">
        <div
          v-for="(val, attr_name, i) in requested_attribute_groups()"
          :key="i"
        >
          <li
            v-for="(name, index) in val.names"
            :key="index"
            class="presentation-attr-value"
          >
            <strong>{{ name }}</strong> :
            {{
              props.presentation.acapy.presentation_exchange.presentation
                .requested_proof.revealed_attr_groups[attr_name].values[name]
                .raw
            }}
            <br />
          </li>
        </div>
        <!-- requested_attributes using 'name' string w/ restrictions -> revealed attributes -->
        <li
          v-for="(val, attr_name, i) in requested_single_attributes()"
          :key="i"
          class="presentation-attr-value"
        >
          <strong>{{ val.name }}</strong>
          :
          {{
            props.presentation.acapy.presentation_exchange.presentation
              .requested_proof.revealed_attrs[attr_name].raw
          }}
        </li>
        <!-- requested_attribute using 'name' string w/o restrictions -> revealed self-attested values -->
        <!-- requested_predicates -> unrevealed attributes -->
      </div>
      <hr />
      <!-- Identifiers -->
      <Accordion>
        <AccordionTab
          v-for="(item, index) in props.presentation.acapy.presentation_exchange
            .presentation.identifiers"
          :key="index"
          :header="`Identifier_${index + 1}`"
        >
          <ul>
            <li v-for="(val, attr_name, i) in item" :key="i">
              <strong>{{ attr_name }}</strong> : {{ val }}
            </li>
          </ul>
        </AccordionTab>
      </Accordion>
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

// four different payload locations for the provided claims based on these filters.

const requested_attribute_groups = (): any => {
  return Object.fromEntries(
    Object.entries(
      props.presentation.acapy.presentation_exchange.presentation_request
        .requested_attributes
    ).filter(([key, ra]: [string, any]): any => {
      return 'names' in ra && 'restrictions' in ra;
    })
  );
};

const requested_single_attributes = (): any => {
  return Object.fromEntries(
    Object.entries(
      props.presentation.acapy.presentation_exchange.presentation_request
        .requested_attributes
    ).filter(([key, ra]: [string, any]): any => {
      return 'name' in ra && 'restrictions' in ra;
    })
  );
};

// to be used in upcoming UX Designed component
// const requested_self_attested_attributes = ():any => {
//   return Object.fromEntries(
//     Object.entries(
//       props.presentation.acapy.presentation_exchange.presentation_request
//         .requested_attributes
//     ).filter(([key, ra]) => {
//       return 'name' in ra && !'restrictions' in ra;
//     })
//   );
// };

// const requested_predicates_attributes = ():any => {
//   return props.presentation.acapy.presentation_exchange.presentation_request
//     .requested_predicates;
// };
</script>

<style>
.presentation-attr-value {
  padding-left: 1em;
}

.pi.pi-check {
  font-size: 18px;
  color: green;
  margin-right: 5px;
}
</style>
