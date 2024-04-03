<template>
  <div v-if="showDidRegister">
    <div v-if="pendingPublicDidTx" class="flex">
      <div class="flex align-items-center mr-2">
        {{ $t('common.status') }}
      </div>
      <div class="flex align-items-center mr-1">
        <StatusChip :status="pendingPublicDidTx.state || ''" />
      </div>
      <div
        v-if="pendingPublicDidTx.state === 'transaction_acked'"
        class="flex align-items-center"
      >
        <Button
          title="Continue Registering Public DID"
          icon="pi pi-file-export"
          class="p-button-rounded p-button-icon-only p-button-text"
          @click="registerPublicDid(true)"
        />
      </div>
    </div>
    <Button
      v-else
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
//Types
import { TransactionRecord } from '@/types/acapyApi/acapyInterface';

// Vue/Primevue
import { computed } from 'vue';
import Button from 'primevue/button';
import StatusChip from '@/components/common/StatusChip.vue';
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
const { endorserConnection, publicDid, walletDids, transactions, writeLedger } =
  storeToRefs(tenantStore);

// Register DID
const registerPublicDid = async (useTxDid = false) => {
  try {
    await tenantStore.registerPublicDid(
      // @ts-expect-error ACApy swagger generation only has meta_data as object
      useTxDid ? pendingPublicDidTx.value?.meta_data?.did : undefined
    );
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
const pendingPublicDidTx = computed<TransactionRecord | null>(() => {
  // If they have a wallet DID but no public, check transactions for a status
  let pending = null;
  if (!hasPublicDid.value && walletDids.value.length > 0) {
    walletDids.value.forEach((wDid) => {
      const pendingTx = transactions.value.find(
        (tx: TransactionRecord) =>
          // @ts-expect-error ACApy swagger generation only has meta_data as object
          tx?.meta_data?.did == wDid.did && tx?.state != 'transaction_accepted'
      );
      if (pendingTx) {
        pending = pendingTx;
      }
    });
  }
  return pending;
});
</script>
