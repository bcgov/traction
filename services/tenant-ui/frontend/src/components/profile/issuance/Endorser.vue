<template>
  <div v-if="canConnectEndorser || hasEndorserConn" class="my-1">
    <p class="my-1">{{ $t('profile.connectTenantToEndorser') }}</p>
    <InputSwitch
      :model-value="hasEndorserConn"
      :disabled="hasEndorserConn"
      @change="connectToEndorser"
    />

    <div v-if="showNotActiveWarn" class="inactive-endorser">
      <i class="pi pi-exclamation-triangle"></i>
      {{ $t('profile.connectionNotActiveYet') }}
      <p class="mt-0 pl-4">
        {{ $t('profile.state', [endorserConnection.state]) }}
      </p>
    </div>

    <div>
      <Accordion>
        <AccordionTab header="Endorser Details">
          <h5 class="my-0">{{ $t('profile.endorserInfo') }}</h5>
          <vue-json-pretty :data="endorserInfo" />
          <h5 class="my-0">{{ $t('profile.endorserConnection') }}</h5>
          <vue-json-pretty
            v-if="endorserConnection"
            :data="endorserConnection"
          />
          <div v-else>{{ $t('profile.tenantNotConnectedToEndorserYet') }}</div>
        </AccordionTab>
      </Accordion>
    </div>
  </div>
  <p v-else class="my-1">
    <i class="pi pi-info-circle"></i>
    {{ $t('profile.connectTenantToEndorserNotAllowed') }}
  </p>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import InputSwitch from 'primevue/inputswitch';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
import { useToast } from 'vue-toastification';
// State
import { useConfigStore, useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';

const toast = useToast();

const { config } = storeToRefs(useConfigStore());
const tenantStore = useTenantStore();
const { endorserConnection, endorserInfo, tenantConfig } =
  storeToRefs(tenantStore);

// Allowed to connect to endorser?
const canConnectEndorser = computed(() => {
  if (tenantConfig.value?.connect_to_endorser?.length) {
    // At this point there's 1 ledger/endorser, check the first and deal with that
    // Will enhance once mult-ledger supported
    const allowedConnection = tenantConfig.value.connect_to_endorser[0];
    if (allowedConnection) {
      // If the tenant is allowed to connect to the configured endorser on the configured ledger
      return (
        allowedConnection.endorser_alias ===
          endorserInfo.value?.endorser_name &&
        allowedConnection.ledger_id ===
          config.value.frontend?.ariesDetails?.ledgerName
      );
    }
  }
  return false;
});

// Connect to endorser
const connectToEndorser = async () => {
  try {
    if (!hasEndorserConn.value) {
      await tenantStore.connectToEndorser();
      // Give a couple seconds to wait for active. If not done by then a message
      // appears to the user saying to refresh themselves
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
