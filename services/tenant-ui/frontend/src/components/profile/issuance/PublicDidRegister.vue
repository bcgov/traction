<template>
  <div v-if="showDidRegister">
    <Button
      title="Register Public DID"
      icon="pi pi-file-export"
      class="p-button-rounded p-button-icon-only p-button-text"
      @click="registerPublicDid()"
    />
  </div>

  <div v-if="showRegistered">
    <i
      v-tooltip="'Public DID has been registered. See details below.'"
      class="pi pi-check-circle text-green-600"
    ></i>
  </div>
</template>

<script setup lang="ts">
// Vue/Primevue
import { computed } from 'vue';
import Button from 'primevue/button';
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';

// Props
const props = defineProps<{
  ledgerInfo: any;
}>();

const toast = useToast();

// State
const tenantStore = useTenantStore();
const { endorserConnection, publicDid, writeLedger } = storeToRefs(tenantStore);

// Register DID
const registerPublicDid = async () => {
  try {
    await tenantStore.registerPublicDid();
    toast.success('Public DID registration sent');
  } catch (error) {
    throw Error(`Failure while registering: ${error}`);
  }
};

// Details about current ledger from the store
const currWriteLedger = computed(() => writeLedger?.value?.ledger_id ?? null);

// Show the DID registration button when the write ledger and endorser are set
const showDidRegister = computed(
  () =>
    props.ledgerInfo.ledger_id === currWriteLedger.value &&
    !hasPublicDid.value &&
    endorserConnection.value?.state === 'active'
);

// Show the DID complete checkmark if it's sucessfull
const hasPublicDid = computed(
  () => !!publicDid.value && !!publicDid.value?.did
);
const showRegistered = computed(
  () =>
    props.ledgerInfo.ledger_id === currWriteLedger.value && hasPublicDid.value
);
</script>
