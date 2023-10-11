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
      filter-display="menu"
      :sort-order="1"
    >
      <template #empty>{{ $t('common.noRecordsFound') }}</template>
      <template #loading>{{ $t('common.loading') }}</template>
      <Column :sortable="false" header="Register">
        <template #body="{ data }">
          <span v-if="isLedgerSet && data.ledger_id === currWriteLedger">
            <i class="pi pi-check-circle"></i>
          </span>
        </template>
      </Column>
      <Column :sortable="true" field="ledger_id" header="Ledger Identifier" />
    </DataTable>

    <div v-if="hasPublicDid" class="true-1">
      <div class="field">
        <label for="didField">{{ $t('profile.publicDid') }}</label>
        <InputText
          id="didField"
          class="w-full"
          readonly
          :value="publicDid.did"
        />
      </div>

      <div class="mt-3">
        <Accordion>
          <AccordionTab header="Public DID Details">
            <h5 class="my-0">{{ $t('profile.publicDid') }}</h5>
            <vue-json-pretty :data="publicDid" />
          </AccordionTab>
        </Accordion>
      </div>
    </div>
  </div>
  <p v-else class="my-1">
    <i class="pi pi-times-circle"></i>
    {{ $t('profile.registerPublicDidNotAllowed') }}
  </p>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
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

// Stores
const tenantStore = useTenantStore();
const { publicDid, tenantConfig, writeLedger, loading } =
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
const isLedgerSet = computed(
  () => !!writeLedger.value && !!writeLedger.value.ledger_id
);
const currWriteLedger = computed(() => {
  if (!!writeLedger.value && !!writeLedger.value.ledger_id) {
    return writeLedger.value.ledger_id;
  }
  return null;
});
// Public DID status
const hasPublicDid = computed(() => !!publicDid.value && !!publicDid.value.did);
</script>

<style lang="scss" scoped>
@import '@/assets/variables.scss';
.p-datatable {
  border-top: 1px solid $tenant-ui-panel-border-color;
}
</style>
