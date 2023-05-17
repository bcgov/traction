<template>
  <div v-if="taaRequired" class="my-1">
    <p>
      <i class="pi pi-exclamation-circle"></i>
      {{ $t('profile.taa.requiredYes') }}
    </p>

    <div v-if="taaAccepted">
      {{ taa.taa_accepted }}
    </div>
    <div v-else>
      <ReviewTaa class="my-2" />
    </div>
  </div>
  <p v-else class="my-1">
    <i class="pi pi-exclamation-circle"></i> {{ $t('profile.taa.requiredNo') }}
  </p>

  <div>
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
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Components
import ReviewTaa from './ReviewTaa.vue';

const toast = useToast();

const tenantStore = useTenantStore();
const { endorserConnection, taa, loadingIssuance } = storeToRefs(tenantStore);

// Display status
const taaAccepted = computed(() => taa.value?.taa_accepted);
const taaRequired = computed(() => taa.value?.taa_required);

// Connect to endorser
const connectToEndorser = async () => {
  try {
    if (!hasEndorserConn.value) {
      await tenantStore.connectToEndorser();
      // Give a couple seconds to wait for active. If not done by then a message
      // appears to the user saying to refresh themselves
      loadingIssuance.value = true;
      await new Promise((r) => setTimeout(r, 2000));
      await tenantStore.getEndorserConnection();
      toast.success('Endorser connection request sent');
    }
  } catch (error) {
    toast.error(`Failure while connecting: ${error}`);
  }
};

// Details about endorser connection
const hasEndorserConn = computed(() => !!endorserConnection.value);
const showNotActiveWarn = computed(
  () => endorserConnection.value && endorserConnection.value.state !== 'active'
);
</script>

<style lang="scss" scoped>
.inactive-endorser {
  color: $tenant-ui-text-warning;
}
</style>
