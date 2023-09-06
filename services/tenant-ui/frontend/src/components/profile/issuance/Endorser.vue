<template>
  <div v-if="canBecomeIssuer" class="my-1">
    <DataTable
      v-model:filters="filter"
      :loading="loading"
      :value="formattedLedgers"
      :paginator="false"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      selection-mode="single"
      data-key="ledger_id"
      sort-field="ledger_id"
      :sort-order="-1"
      filter-display="menu"
    >
      <template #header>
        <div class="flex justify-content-between">
          <div class="flex justify-content-start"></div>
          <div class="flex justify-content-end">
            <span class="p-input-icon-left">
              <i class="pi pi-search ml-0" />
              <InputText
                v-model="filter.global.value"
                placeholder="Search Endorsers"
              />
            </span>
          </div>
        </div>
      </template>
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :sortable="false" header="Actions">
        <template #body="{ data }">
          <span v-if="isLedgerSet && data.ledger_id === currWriteLedger">
            <i class="pi pi-check-circle p-tag-success"></i>
          </span>
          <span
            v-if="
              !isLedgerSet ||
              (isLedgerSet &&
                enableLedgerSwitch &&
                data.ledger_id !== currWriteLedger)
            "
          >
            <Button
              :label="$t('profile.connectToEndorserAndRegisterDID')"
              icon="pi pi-check-square"
              class="p-button-rounded p-button-icon-only p-button-text"
              @click="connecttoLedger(data.ledger_id)"
            />
          </span>
        </template>
      </Column>
      <Column
        :sortable="true"
        field="ledger_id"
        header="Ledger Identifier"
        filter-field="ledger_id"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Ledger"
            @input="filterCallback()"
          />
        </template>
      </Column>
      <Column
        :sortable="true"
        field="endorser_alias"
        header="Endorser Alias"
        filter-field="endorser_alias"
        :show-filter-match-modes="false"
      >
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            class="p-column-filter"
            placeholder="Search By Endorser"
            @input="filterCallback()"
          />
        </template>
      </Column>
    </DataTable>
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
    <i class="pi pi-times-circle"></i>
    {{ $t('profile.connectTenantToEndorserNotAllowed') }}
  </p>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import DataTable, { DataTableFilterMetaData } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Column from 'primevue/column';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
import { useToast } from 'vue-toastification';
// State
import { useTenantStore } from '@/store';
import { TABLE_OPT } from '@/helpers/constants';
import { storeToRefs } from 'pinia';

const toast = useToast();

const tenantStore = useTenantStore();
const { endorserConnection, endorserInfo, tenantConfig, writeLedger, loading } =
  storeToRefs(tenantStore);
const endorserArr = tenantConfig.value.connect_to_endorser.map(
  (config: any) => ({
    ledger_id: config.ledger_id,
    endorser_alias: config.endorser_alias,
  })
);
const formattedLedgers = computed(() => endorserArr);

// Allowed to connect to endorser and register DID?
const canBecomeIssuer = computed(() => {
  if (
    tenantConfig.value?.connect_to_endorser?.length &&
    tenantConfig.value?.create_public_did?.length
  ) {
    return true;
  }
  return false;
});

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
    await waitForActiveEndorserConnection();
    await tenantStore.getEndorserConnection();
    toast.success('Endorser connection request sent');
  } catch (error) {
    throw Error(`Failure while connecting: ${error}`);
  }
};

const waitForActiveEndorserConnection = async () => {
  const connId = endorserConnection.value.connection_id;
  let retries = 0;
  for (;;) {
    const connState = await tenantStore.getEndorserConnectionState(connId);
    if (connState === 'active') {
      console.log(`Endorser connection ${connId} state is active`);
      return;
    }
    retries = retries + 1;
    const wait_interval = Math.pow(3, 1 + 0.25 * (retries - 1));
    await new Promise((r) => setTimeout(r, wait_interval));
  }
};

// Register DID
const registerPublicDid = async () => {
  try {
    const createdDID = await tenantStore.registerPublicDid();
    if (createdDID) {
      await tenantStore.assignPublicDid(createdDID);
      toast.success('Public DID registration sent');
    } else {
      toast.error('Unable to post DID to ledger');
    }
  } catch (error) {
    throw Error(`Failure while registering: ${error}`);
  }
};

// Details about endorser connection
const hasEndorserConn = computed(() => !!endorserConnection.value);
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

const filter = ref({
  global: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  ledger_id: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
  endorser_alias: {
    value: null,
    matchMode: FilterMatchMode.CONTAINS,
  } as DataTableFilterMetaData,
});
</script>

<style lang="scss" scoped>
.inactive-endorser {
  color: $tenant-ui-text-warning;
}
</style>
