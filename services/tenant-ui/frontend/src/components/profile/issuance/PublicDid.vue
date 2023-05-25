<template>
  <div v-if="canRegisterDid" class="true-1">
    <p class="my-1">{{ $t('profile.registerPublicDid') }}</p>
    <InputSwitch
      :model-value="hasPublicDid"
      :disabled="endorserNotActive || hasPublicDid"
      @change="registerPublicDid"
    />

    <!-- DID -->
    <div v-if="hasPublicDid" class="field">
      <label for="didField">{{ $t('profile.publicDid') }}</label>
      <InputText id="didField" class="w-full" readonly :value="publicDid.did" />
    </div>

    <div>
      <Accordion>
        <AccordionTab header="Public DID Details">
          <h5 class="my-0">{{ $t('profile.publicDid') }}</h5>
          <vue-json-pretty :data="publicDid" />
        </AccordionTab>
      </Accordion>
    </div>
  </div>
  <p v-else class="my-1">
    <i class="pi pi-info-circle"></i>
    {{ $t('profile.registerPublicDidNotAllowed') }}
  </p>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import InputSwitch from 'primevue/inputswitch';
import InputText from 'primevue/inputtext';
import VueJsonPretty from 'vue-json-pretty';
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';

const toast = useToast();

// Tenant store
const tenantStore = useTenantStore();
const { endorserConnection, publicDid } = storeToRefs(tenantStore);

// Register DID
const canRegisterDid = ref(true); // to be determined
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
const hasPublicDid = computed(() => !!publicDid.value && !!publicDid.value.did);

// Details about endorser connection
const endorserNotActive = computed(
  () => !endorserConnection.value || endorserConnection.value.state !== 'active'
);
</script>
