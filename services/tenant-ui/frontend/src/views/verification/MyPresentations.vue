<script setup lang="ts">
import verifierPresentations from '../../components/verifier/Presentations.vue';
import SuperYou from '@/components/common/SuperYou.vue';

const apiUrl = '/tenant/v1/verifier/presentations/adhoc-request';

const templateJson = {
  contact_id: '67f68781-4dd9-49ad-9a5e-1e9a06e901f4',
  connection_id: '6530a727-8c05-4818-a1bb-687117afbd44',
  proof_request: {
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
  name: 'string',
  version: '1.0.0',
  external_reference_id: 'string',
  comment: 'string',
  tags: [],
};
</script>

<template>
  <div class="presentation-request-btn">
    <SuperYou
      :api-url="apiUrl"
      :template-json="templateJson"
      text="Create Presentation Request"
      icon="pi-key"
    />
  </div>
  <verifierPresentations />
</template>

<style scoped>
.presentation-request-btn {
  float: right;
}
</style>
