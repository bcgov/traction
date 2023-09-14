<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <DataTable
      :loading="loading"
      :value="endorser_ledger_config"
      :paginator="true"
      :rows="TABLE_OPT.ROWS_DEFAULT"
      :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
      selection-mode="single"
      data-key="ledger_id"
      filter-display="menu"
    >
      <Column
        :sortable="false"
        field="ledger_id"
        header="Ledger Identifier"
        :show-filter-match-modes="false"
      ></Column>
      <Column
        :sortable="false"
        field="endorser_alias"
        header="Endorser Alias"
        :show-filter-match-modes="false"
      ></Column>
    </DataTable>
    <!-- Can become an issuer -->
    <div class="field">
      <label for="canBecomeIssuer">
        {{ $t('tenants.settings.canBecomeIssuer') }}
      </label>
      <InputSwitch id="canBecomeIssuer" v-model="v$.canBecomeIssuer.$model" />
    </div>

    <!-- Can switch endorser/ledger -->
    <div class="field">
      <label for="enableLedgerSwitch">
        {{ $t('tenants.settings.enableLedgerSwitch') }}
      </label>
      <InputSwitch
        id="enableLedgerSwitch"
        v-model="v$.enableLedgerSwitch.$model"
      />
    </div>

    <Button
      type="submit"
      :label="$t('common.submit')"
      class="w-full"
      :disabled="loading || loadingEndorser"
    />
  </form>
</template>

<script setup lang="ts">
// Types
import { TenantRecord } from '@/types/acapyApi/acapyInterface';

// Vue
import { onMounted, reactive, ref, Ref, computed } from 'vue';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputSwitch from 'primevue/inputswitch';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
// State
import {
  useConfigStore,
  useInnkeeperTenantsStore,
  useTenantStore,
} from '@/store';
import { TABLE_OPT } from '@/helpers/constants';
import { storeToRefs } from 'pinia';

const toast = useToast();

const emit = defineEmits(['closed', 'success']);

const innkeeperTenantsStore = useInnkeeperTenantsStore();
const tenantStore = useTenantStore();
const { loading, defaultConfigValues } = storeToRefs(
  useInnkeeperTenantsStore()
);
// For the innkeeper tenant, reuse here for getting configured endorser
const {
  endorserInfo,
  tenantConfig,
  loading: loadingEndorser,
} = storeToRefs(useTenantStore());

// Props
const props = defineProps<{
  tenant: TenantRecord;
}>();

// Validation
const formFields = reactive({
  canBecomeIssuer: false,
  enableLedgerSwitch: false,
});
const rules = {
  canBecomeIssuer: {},
  enableLedgerSwitch: {},
};
const v$ = useVuelidate(rules, formFields);

// URL Form submission
const submitted = ref(false);
let endorser_ledger_config: any = [];
if (tenantConfig.value?.connect_to_endorser?.length) {
  endorser_ledger_config = computed(() =>
    tenantConfig.value.connect_to_endorser.map((config: any) => ({
      ledger_id: config.ledger_id,
      endorser_alias: config.endorser_alias,
    }))
  );
} else {
  await innkeeperTenantsStore.getDefaultConfigValues();
  endorser_ledger_config = computed(() => {
    return defaultConfigValues.value.connected_to_endorsers;
  });
}
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  let connect_to_endorser_payload = [];
  let create_public_did_payload = [];
  if (tenantConfig.value?.connect_to_endorser?.length) {
    connect_to_endorser_payload = tenantConfig.value.connect_to_endorser;
  } else {
    connect_to_endorser_payload =
      defaultConfigValues.value.connected_to_endorsers;
  }
  if (tenantConfig.value?.create_public_did?.length) {
    create_public_did_payload = tenantConfig.value.create_public_did;
  } else {
    create_public_did_payload = defaultConfigValues.value.created_public_did;
  }
  try {
    await innkeeperTenantsStore.updateTenantConfig(props.tenant.tenant_id, {
      connect_to_endorser: formFields.canBecomeIssuer
        ? connect_to_endorser_payload
        : [],
      create_public_did: formFields.canBecomeIssuer
        ? create_public_did_payload
        : [],
      enable_ledger_switch: formFields.enableLedgerSwitch ? true : false,
    });
    toast.success('Tenant Settings Updated');
    emit('success');
    // close up on success
    emit('closed');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};

onMounted(() => {
  // Determine if the Tenant already has the config permission
  // This will change in the future for multi-ledger support but
  // for now determine by the fields being set.
  formFields.canBecomeIssuer =
    !!props.tenant.connect_to_endorser?.length &&
    !!props.tenant.created_public_did?.length;
  formFields.enableLedgerSwitch = !!props.tenant.enable_ledger_switch;

  // Fetch the configured instance endorser details
  tenantStore.getEndorserInfo();
});
</script>
