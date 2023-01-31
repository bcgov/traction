<template>
  <p class="my-1">Connect Tenant To Endorser</p>
  <InputSwitch
    :model-value="hasEndorserConn"
    :disabled="hasEndorserConn"
    @change="connectToEndorser"
  />

  <div v-if="showNotActiveWarn" class="inactive-endorser">
    <i class="pi pi-exclamation-triangle"></i>
    Connection not Active yet, refresh or come back later.
    <p class="mt-0 pl-4">State: {{ endorserConnection.state }}</p>
  </div>

  <div>
    <Accordion>
      <AccordionTab header="Endorser Details">
        <h5 class="my-0">Endorser Info</h5>
        <vue-json-pretty :data="endorserInfo" />
        <h5 class="my-0">Endorser Connection</h5>
        <vue-json-pretty v-if="endorserConnection" :data="endorserConnection" />
        <div v-else>Tenant not connected to Endorser yet</div>
      </AccordionTab>
    </Accordion>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import InputSwitch from 'primevue/inputswitch';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';

const toast = useToast();

const tenantStore = useTenantStore();
const { endorserConnection, endorserInfo, loadingIssuance } =
  storeToRefs(tenantStore);

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
