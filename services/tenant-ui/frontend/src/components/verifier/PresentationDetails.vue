<template>
  <div v-if="presentation">
    <ul>
      <li>Status: {{ presentation.status }}</li>
      <li>Updated at: {{ presentation.updated_at }}</li>
      <li>Contact Alias: {{ presentation.contact.alias }}</li>
      <hr />
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
    </ul>
  </div>
  <div v-else>...loading</div>
</template>

<script setup lang="ts">
import { PropType } from 'vue';

const props = defineProps({
  presentation: {
    type: Object as PropType<any>,
    required: true,
  },
});
</script>

<style>
.presentation-attr-value {
  padding-left: 1em;
}
</style>
