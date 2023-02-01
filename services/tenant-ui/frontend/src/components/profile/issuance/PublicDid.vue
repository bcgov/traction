<template>
  <p class="my-1">Register a public DID</p>
  <InputSwitch
    :model-value="hasPublicDid"
    :disabled="endorserNotActive || hasPublicDid"
    @change="registerPublicDid"
  />

  <!-- DID -->
  <div v-if="hasPublicDid" class="field">
    <label for="didField">Public DID</label>
    <InputText
      id="didField"
      class="w-full"
      readonly
      :value="publicDid.result.did"
    />
  </div>

  <div>
    <Accordion>
      <AccordionTab header="Public DID Details">
        <h5 class="my-0">Public DID</h5>
        <vue-json-pretty :data="publicDid" />
      </AccordionTab>
    </Accordion>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import InputSwitch from 'primevue/inputswitch';
import InputText from 'primevue/inputtext';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';

const toast = useToast();

// Tenant store
const tenantStore = useTenantStore();
const { endorserConnection, publicDid } = storeToRefs(tenantStore);

// Connect to endorser
const registerPublicDid = async () => {
  try {
    if (!hasPublicDid.value) {
      await tenantStore.registerPublicDid();
      toast.success('Public DID registration sent');
    }
  } catch (error) {
    toast.error(`Failure while registering: ${error}`);
  }
};

// Public DID status
const hasPublicDid = computed(
  () => !!publicDid.value && !!publicDid.value.result
);

// Details about endorser connection
const endorserNotActive = computed(
  () => !endorserConnection.value || endorserConnection.value.state !== 'active'
);
</script>
