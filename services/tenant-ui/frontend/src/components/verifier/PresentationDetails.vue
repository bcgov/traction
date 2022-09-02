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
      <div v-if="presentation.acapy.presentation_exchange.presentation">
        <!-- PRESENTATION RECEIVED-->
        <!-- requested_attributes using 'names' list -> revealed attribute groups -->
        <li
          v-for="(value, attr, index) in props.presentation.acapy
            .presentation_exchange.presentation.requested_proof
            .revealed_attr_groups"
          :key="index"
        >
          <h4>{{ attr }}:</h4>
          <span
            v-for="(val, attr_name, i) in value.values"
            :key="i"
            class="presentation-attr-value"
          >
            <b>{{ attr_name }}</b> : {{ val.raw }}
            <br />
          </span>
        </li>
        <!-- requested_attributes using 'name' string w/ restrictions -> revealed attributes -->
        <li
          v-for="(val, attr_name, i) in presentation.acapy.presentation_exchange
            .presentation.requested_proof.revealed_attrs"
          :key="i"
          class="presentation-attr-value"
        >
          <b>{{
            presentation.acapy.presentation_exchange.presentation_request
              .requested_attributes[attr_name].name
          }}</b>
          : {{ val.raw }}
        </li>
        <!-- requested_attribute using 'name' string w/o restrictions -> revealed self-attested values -->
        <!-- requested_predicates -> unrevealed attributes -->
      </div>
    </ul>
  </div>
  <div v-else>...loading</div>
</template>

<script setup lang="ts">
import { PropType } from 'vue';
import { formatDateLong } from '@/helpers';

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
});
</script>

<style>
.presentation-attr-value {
  padding-left: 1em;
}
</style>
