<template>
  <div v-if="canBecomeIssuer" class="my-1">
    <DataTable
      v-model:loading="loading"
      :value="endorserList"
      :paginator="false"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      selection-mode="single"
      data-key="ledger_id"
      sort-field="ledger_id"
      filter-display="menu"
      :sort-order="1"
    >
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :sortable="false" header="Connect">
        <template #body="{ data }">
          <EndorserConnect :ledgerInfo="data"/>
        </template>
      </Column>
      <Column :sortable="true" field="ledger_id" header="Ledger" />
      <Column :sortable="true" field="endorser_alias" header="Alias" />
    </DataTable>
    <div v-if="showNotActiveWarn" class="inactive-endorser">
      <i class="pi pi-exclamation-triangle"></i>
      {{ $t('profile.connectionNotActiveYet') }}
      <p class="mt-0 pl-4">
        {{ $t('profile.state', [endorserConnection.state]) }}
      </p>
    </div>

    <div class="mt-3">
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
    <i class="pi pi-times-circle"></i>
    {{ $t('profile.connectTenantToEndorserNotAllowed') }}
  </p>
</template>

<script setup lang="ts">
// Vue
import { computed } from 'vue';
// PrimeVue
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { TABLE_OPT } from '@/helpers/constants';
import { storeToRefs } from 'pinia';
// Other Components
import EndorserConnect from './EndorserConnect.vue';

const toast = useToast();

const tenantStore = useTenantStore();
const { endorserConnection, endorserInfo, tenantConfig, writeLedger, loading } =
  storeToRefs(tenantStore);
const endorserList = tenantConfig.value.connect_to_endorser.map(
  (config: any) => ({
    ledger_id: config.ledger_id,
    endorser_alias: config.endorser_alias,
  })
);

// Allowed to connect to endorser and register DID?
const canBecomeIssuer = computed(
  () =>
    tenantConfig.value?.connect_to_endorser?.length &&
    tenantConfig.value?.create_public_did?.length
);

const connecttoLedger = async (ledger_id: string) => {
  let prevLedgerId: any = undefined;
  if (!!writeLedger.value && !!writeLedger.value.ledger_id) {
    prevLedgerId = writeLedger.value.ledger_id;
  }
  try {
    await tenantStore.setWriteLedger(ledger_id);
    await connectToEndorser();
    await registerPublicDid();
  } catch (error) {
    if (prevLedgerId) {
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
const connectToEndorser = async () => {
  try {
    await tenantStore.connectToEndorser();
    // Give a couple seconds to wait for active. If not done by then
    // a message appears to the user saying to refresh themselves
    await tenantStore.waitForActiveEndorserConnection();
    await tenantStore.getEndorserConnection();
    toast.success('Endorser connection request sent');
  } catch (error) {
    throw Error(`Failure while connecting: ${error}`);
  }
};

// Register DID
const registerPublicDid = async () => {
  try {
    await tenantStore.registerPublicDid();
    toast.success('Public DID registration sent');
  } catch (error) {
    throw Error(`Failure while registering: ${error}`);
  }
};

// Details about endorser connection
const showNotActiveWarn = computed(
  () => endorserConnection.value && endorserConnection.value.state !== 'active'
);
const isLedgerSet = computed(
  () => !!writeLedger.value && !!writeLedger.value.ledger_id
);
// Handler failure logic
const currWriteLedger = computed(() => {
  if (!!writeLedger.value && !!writeLedger.value.ledger_id) {
    return writeLedger.value.ledger_id;
  }
  return null;
});
const enableLedgerSwitch = computed(
  () => tenantConfig.value.enable_ledger_switch
);
</script>

<style lang="scss" scoped>
@import '@/assets/variables.scss';
.inactive-endorser {
  color: $tenant-ui-text-warning;
}

.p-datatable {
  border-top: 1px solid $tenant-ui-panel-border-color;
}
</style>
