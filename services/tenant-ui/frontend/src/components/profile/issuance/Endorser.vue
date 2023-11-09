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
      :sort-order="1"
    >
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :sortable="false" header="Connect">
        <template #body="{ data }">
          <EndorserConnect :ledger-info="data" />
        </template>
      </Column>
      <Column :sortable="true" field="ledger_id" header="Ledger" />
      <Column :sortable="true" field="endorser_alias" header="Alias">
        <template #body="{ data }">
          {{ data.endorser_alias }}
          <span
            v-if="
              config.frontend.quickConnectEndorserName === data.endorser_alias
            "
            class="ml-1"
          >
            <i
              v-tooltip="
                'This Endorser is marked as Quick-Connect (auto accept/endorse)'
              "
              class="pi pi-bolt"
              style="font-size: 0.8rem"
            ></i>
          </span>
        </template>
      </Column>
    </DataTable>
    <div v-if="showNotActiveWarn" class="inactive-endorser">
      <i class="pi pi-exclamation-triangle"></i>
      {{ $t('profile.connectionNotActiveYet') }}
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
// State
import { useConfigStore, useTenantStore } from '@/store';
import { TABLE_OPT } from '@/helpers/constants';
import { storeToRefs } from 'pinia';
// Other Components
import EndorserConnect from './EndorserConnect.vue';

const configStore = useConfigStore();
const tenantStore = useTenantStore();
const { config } = storeToRefs(configStore);
const { endorserConnection, endorserInfo, tenantConfig, loading } =
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

// Details about endorser connection
const showNotActiveWarn = computed(
  () => endorserConnection.value && endorserConnection.value.state !== 'active'
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
