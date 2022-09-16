<template>
  <RowExpandData :loading="loading" :data="item">
    <template #details="presentation">
      <div>
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
            <span class="pi pi-check"></span><span>Credential is valid</span
            ><br />
            <span class="pi pi-check"></span
            ><span>Credential is tamper-free </span><br />
            <span class="pi pi-check"></span
            ><span>All attribute restrictions were satisfied</span><br />
            <hr />
          </div>
          <VerifiedPresentationData
            v-if="presentation.status == 'verified'"
            :presentation="presentation"
          />
        </ul>
      </div>
    </template>
  </RowExpandData>
</template>

<script async setup lang="ts">
// Vue
import { PropType } from 'vue';
// PrimeVue
// State
// Other components
import { formatDateLong } from '@/helpers';
import RowExpandData from '../common/RowExpandData.vue';
import VerifiedPresentationData from './VerifiedPresentationData.vue';
import useGetVerifierPresentation from '@/composables/useGetVerifierPresentation';

const props = defineProps({
  row: {
    type: null as unknown as PropType<any>,
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

const { loading, item, fetchItemWithAcapy } = useGetVerifierPresentation();

fetchItemWithAcapy(props.row.verifier_presentation_id);
</script>

<style scoped></style>
