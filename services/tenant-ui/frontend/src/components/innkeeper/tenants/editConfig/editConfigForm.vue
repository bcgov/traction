<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <p class="my-0">
      <strong>{{ $t('tenants.settings.ledgerName') }} </strong>
      {{ config.frontend?.ariesDetails?.ledgerName }}
    </p>
    <p class="mt-0">
      <strong> {{ $t('tenants.settings.endorserAlias') }} </strong>
      {{ endorserInfo?.endorser_name }}
    </p>
    <!-- Can Connect to endorser -->
    <div class="field">
      <label for="canConnectEndorser">
        {{ $t('tenants.settings.canConnectEndorser') }}
      </label>
      <InputSwitch
        id="canConnectEndorser"
        v-model="v$.canConnectEndorser.$model"
      />
    </div>

    <!-- Can register public DID -->
    <div class="field">
      <label for="canRegisterDid">
        {{ $t('tenants.settings.canRegisterDid') }}
      </label>
      <InputSwitch id="canRegisterDid" v-model="v$.canRegisterDid.$model" />
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
import { onMounted, reactive, ref } from 'vue';
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
import { storeToRefs } from 'pinia';

const toast = useToast();

const emit = defineEmits(['closed', 'success']);

const { config } = storeToRefs(useConfigStore());
const { loading } = storeToRefs(useInnkeeperTenantsStore());
const innkeeperTenantsStore = useInnkeeperTenantsStore();
// For the innkeeper tenant, reuse here for getting configured endorser
const tenantStore = useTenantStore();
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
  canConnectEndorser: false,
  canRegisterDid: false,
});
const rules = {
  canConnectEndorser: {},
  canRegisterDid: {},
};
const v$ = useVuelidate(rules, formFields);

// URL Form submission
const submitted = ref(false);
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
    connect_to_endorser_payload = [
      {
        endorser_alias: endorserInfo.value?.endorser_name || '',
        ledger_id: config.value.frontend?.ariesDetails?.ledgerName,
      },
    ];
  }
  if (tenantConfig.value?.create_public_did?.length) {
    create_public_did_payload = tenantConfig.value.create_public_did;
  } else {
    create_public_did_payload = [
      config.value.frontend?.ariesDetails?.ledgerName,
    ];
  }
  try {
    await innkeeperTenantsStore.updateTenantConfig(props.tenant.tenant_id, {
      connect_to_endorser: formFields.canConnectEndorser
        ? connect_to_endorser_payload
        : [],
      create_public_did: formFields.canRegisterDid
        ? create_public_did_payload
        : [],
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
  formFields.canConnectEndorser = !!props.tenant.connect_to_endorser?.length;
  formFields.canRegisterDid = !!props.tenant.created_public_did?.length;

  // Fetch the configured instance endorser details
  tenantStore.getEndorserInfo();
});
</script>
