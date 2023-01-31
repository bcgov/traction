<template>
  <p class="my-1">Connect Tenant To Endorser</p>
  <InputSwitch
    :modelValue="hasEndorserConn"
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
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';

const tenantStore = useTenantStore();
const { endorserConnection, endorserInfo } = storeToRefs(tenantStore);

// Connect to endorser
const connectToEndorser = () => {
  if (!hasEndorserConn.value) {
    tenantStore.connectToEndorser();
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
