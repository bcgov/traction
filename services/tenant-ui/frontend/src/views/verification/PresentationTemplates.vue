<template>
  <h3>Presentation Templates</h3>
  Coming Soon
  <div class="api-custom-btn">
    <SuperYou :api-url="apiUrl" :template-json="templateJson" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import SuperYou from '@/components/common/SuperYou.vue';
import { API_PATH } from '@/helpers/constants';

/**
 * Convenient functionality for devs to test the API
 */
const templateJson = ref({
  name: 'string',
  external_reference_id: 'string',
  comment: 'string',
  tags: [],
  presentation_request: {
    requested_attributes: [
      {
        name: 'string',
        names: ['string'],
        non_revoked: {},
        restrictions: [{}],
      },
    ],
    requested_predicates: [
      {
        name: 'string',
        p_type: '<',
        p_value: 0,
        non_revoked: {},
        restrictions: [{}],
      },
    ],
    non_revoked: {},
  },
});
const apiUrl = ref(API_PATH.VERIFIER_PRESENTATION_TEMPLATES);
</script>
