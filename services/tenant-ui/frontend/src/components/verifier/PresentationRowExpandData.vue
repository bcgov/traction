<template>
  <RowExpandData
    :url="API_PATH.PRESENT_PROOF_RECORD(props.row.verifier_presentation_id)"
    :params="{ acapy: true }"
  >
    <template #details="presentation">
      <div>
        <ul>
          <div v-if="props.header">
            <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
            <li>{{ $t('verifier.status') }}: {{ presentation.status }}</li>
            <li>
              <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
              {{ $t('verifier.updatedAt') }}:
              {{ formatDateLong(presentation.updated_at) }}
            </li>
            <li>
              <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
              {{ $t('verifier.contactAlias') }}:
              {{ presentation.contact.alias }}
            </li>
            <hr />
          </div>
          <!-- What does verified mean -->
          <div
            v-if="props.showInformation && presentation.status == 'verified'"
            class="information"
          >
            <span class="pi pi-check"></span
            ><span>
              {{ $t('verifier.credentialHeldBy') }}
              <strong>{{ presentation.contact.alias }}</strong></span
            ><br />
            <span class="pi pi-check"></span
            ><span>{{ $t('verifier.credentialValid') }}</span
            ><br />
            <span class="pi pi-check"></span
            ><span>{{ $t('verifier.credentialTamperFree') }}</span
            ><br />
            <span class="pi pi-check"></span
            ><span>{{ $t('verifier.attributeRestrictionsSatisfied') }}</span
            ><br />
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
import { API_PATH } from '@/helpers/constants';

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
</script>

<style scoped></style>
