<template>
  <div v-if="canBecomeIssuer" class="my-1">
    <DataTable
      v-model:loading="loading"
      :value="formattedLedgers"
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
      <Column :sortable="false" header="Register">
        <template #body="{ data }">
          <PublicDidRegister :ledger-info="data" />
        </template>
      </Column>
      <Column :sortable="true" field="ledger_id" header="Ledger Identifier" />
    </DataTable>

    <div v-if="!hasPublicDid && pendingPublicDidTx" class="pending-did">
      <i class="pi pi-exclamation-triangle mr-1"></i>
      <span v-if="pendingPublicDidTx.state === 'transaction_acked'">{{
        $t('profile.didNotActiveApproved')
      }}</span>
      <span v-else>{{ $t('profile.didNotActiveYet') }}</span>
    </div>

    <div v-if="hasPublicDid" class="field mt-2">
      <label for="didField">{{ $t('profile.publicDid') }}</label>
      <InputText id="didField" class="w-full" readonly :value="publicDid.did" />
    </div>
    <div v-else-if="pendingPublicDidTx" class="field mt-2">
      <label for="didField">{{ $t('profile.publicDidPending') }}</label>
      <InputText
        id="didField"
        class="w-full"
        readonly
        :value="pendingPublicDidTx.meta_data?.did"
      />
    </div>

    <div class="mt-3">
      <Accordion>
        <AccordionTab header="Public DID Details">
          <h5 class="my-0">{{ $t('profile.publicDid') }}</h5>
          <vue-json-pretty :data="publicDid" />

          <div v-if="pendingPublicDidTx">
            <h5 class="mt-4 mb-0">{{ $t('profile.pendingDidTx') }}</h5>
            <vue-json-pretty :data="pendingPublicDidTx as any" />
          </div>
        </AccordionTab>
      </Accordion>
    </div>
  </div>
  <p v-else class="my-1">
    <i class="pi pi-times-circle"></i>
    {{ $t('profile.registerPublicDidNotAllowed') }}
  </p>
</template>

<script setup lang="ts">
// Vue/Primevue/etc
import { computed } from 'vue';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import VueJsonPretty from 'vue-json-pretty';
// State
import { useTenantStore } from '@/store';
import { TABLE_OPT } from '@/helpers/constants';
import { storeToRefs } from 'pinia';
// Other Components
import PublicDidRegister from './PublicDidRegister.vue';

// Stores
const tenantStore = useTenantStore();
const { publicDid, tenantConfig, loading, pendingPublicDidTx } =
  storeToRefs(tenantStore);

const canBecomeIssuer = computed(
  () =>
    tenantConfig.value?.connect_to_endorser?.length &&
    tenantConfig.value?.create_public_did?.length
);
const formattedLedgers = computed(() =>
  tenantConfig.value.create_public_did.map((ledger: any) => ({
    ledger_id: ledger,
  }))
);
// Public DID status
const hasPublicDid = computed(() => !!publicDid.value && !!publicDid.value.did);
</script>

<style lang="scss" scoped>
.p-datatable {
  border-top: 1px solid $tenant-ui-panel-border-color;
}
.pending-did {
  color: $tenant-ui-text-warning;
}
</style>
