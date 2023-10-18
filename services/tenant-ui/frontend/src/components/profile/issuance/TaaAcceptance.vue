<template>
  <div v-if="taaRequired" class="my-1">
    <div v-if="taaAccepted">
      <p>
        <i class="pi pi-check-circle accept-icon"></i>
        {{ $t('profile.taa.accepted') }}
        <strong>
          {{ formatUnixDate(taa.taa_accepted.time) }}
        </strong>
      </p>
    </div>
    <div v-else>
      <p>
        <i class="pi pi-info-circle"></i>
        {{ $t('profile.taa.requiredYes') }}
      </p>
      <ReviewTaa class="my-2" />
    </div>
  </div>
  <p v-else class="my-1">
    <i class="pi pi-info-circle"></i> {{ $t('profile.taa.requiredNo') }}
  </p>

  <div v-if="taaRequired">
    <Accordion>
      <AccordionTab :header="$t('profile.taa.taaDetails')">
        <h5 class="my-0">{{ $t('profile.taa.taaDetails') }}</h5>
        <vue-json-pretty :data="taa" />
      </AccordionTab>
    </Accordion>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Components
import ReviewTaa from './ReviewTaa.vue';
import { formatUnixDate } from '@/helpers';

const tenantStore = useTenantStore();
const { taa } = storeToRefs(tenantStore);

// Display status
const taaAccepted = computed(() => taa.value?.taa_accepted);
const taaRequired = computed(() => taa.value?.taa_required);
</script>

<style lang="scss" scoped>
.accept-icon {
  color: green;
}
</style>
