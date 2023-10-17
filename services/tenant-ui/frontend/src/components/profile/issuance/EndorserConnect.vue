<template>
  <div v-if="showEndorserConnect">
    <Button
      title="Connect to endorser"
      icon="pi pi-user-plus"
      class="p-button-rounded p-button-icon-only p-button-text"
      @click="
        connectToLedger(
          props.ledgerInfo.endorser_alias,
          props.ledgerInfo.ledger_id
        )
      "
    />
  </div>

  <div
    v-if="endorserConnection && props.ledgerInfo.ledger_id === currWriteLedger"
    class="flex"
  >
    <div class="flex align-items-center mr-2">{{ $t('common.status') }}</div>
    <div class="flex align-items-center mr-1">
      <StatusChip :status="endorserConnection.state" />
    </div>
    <div v-if="canDeleteConnection" class="flex align-items-center">
      <Button
        title="Delete Connection"
        icon="pi pi-trash"
        class="p-button-rounded p-button-icon-only p-button-text"
        @click="deleteConnection($event, endorserConnection.connection_id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// Vue/Primevue
import { computed } from 'vue';
import Button from 'primevue/button';
import { useToast } from 'vue-toastification';
import { useConfirm } from 'primevue/useconfirm';
// State
import { useConfigStore, useConnectionStore, useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other Components
import StatusChip from '@/components/common/StatusChip.vue';

// Props
const props = defineProps<{
  ledgerInfo: any;
}>();

const confirm = useConfirm();
const toast = useToast();

// State
const configStore = useConfigStore();
const connectionStore = useConnectionStore();
const tenantStore = useTenantStore();
const { config } = storeToRefs(configStore);
const { endorserConnection, publicDid, tenantConfig, writeLedger } =
  storeToRefs(tenantStore);

// Set the write ledger and then connect to the relevant endorser
const connectToLedger = async (
  endorser_alias: string,
  ledger_id: string,
  switchLeger = false
) => {
  // Track the current connected to ledger (or undefined if none)
  const prevLedgerId = writeLedger?.value?.ledger_id;
  try {
    const quickConnect =
      config.value.frontend.quickConnectEndorserName === endorser_alias;
    await tenantStore.setWriteLedger(ledger_id);
    await connectToEndorser(quickConnect);
    if (quickConnect) {
      await registerPublicDid();
    }
  } catch (error) {
    // If we're switching ledgers, and it fails, revert to the old one
    if (prevLedgerId && switchLeger) {
      try {
        await tenantStore.setWriteLedger(prevLedgerId);
        await connectToEndorser();
      } catch (endorserError) {
        toast.error(`${endorserError}`);
      }
      toast.error(
        `${error}, reverting to previously set ledger ${prevLedgerId}`
      );
    } else {
      toast.error(`${error}`);
    }
  }
};

// Connect to endorser
const connectToEndorser = async (quickConnect = false) => {
  try {
    await tenantStore.connectToEndorser(quickConnect);
    toast.success('Endorser connection request sent');
  } catch (error) {
    throw Error(`Failure while connecting: ${error}`);
  }
};

// Register DID (only for "quick connect")
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

// Show the endorser connection button when...
const showEndorserConnect = computed(() => {
  //... no current write ledger or endorser conn is set
  if (!currWriteLedger.value || !endorserConnection.value) {
    return true;
  }
  //... the write ledger IS set but there's no connection to it's endorser
  if (
    !endorserConnection.value &&
    props.ledgerInfo.ledger_id === currWriteLedger.value
  ) {
    return true;
  }
  //... you're allowed to Switch ledgers
  if (
    tenantConfig.value.enable_ledger_switch &&
    props.ledgerInfo.ledger_id !== currWriteLedger.value
  ) {
    return true;
  }
  //... otherwise don't
  return false;
});

// Can delete connection
const hasPublicDid = computed(() => !!publicDid.value && !!publicDid.value.did);
const canDeleteConnection = computed(
  () => endorserConnection.value?.state !== 'active' || !hasPublicDid.value
);

// Delete endorser connection
const deleteConnection = (event: any, id: string) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to disconnect from this Endorser?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      doDelete(id);
    },
  });
};
const doDelete = (id: string) => {
  connectionStore
    .deleteConnection(id)
    .then(() => {
      tenantStore.getEndorserConnection();
      toast.success(`Endorser Connection Removed`);
    })
    .catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
};
</script>
