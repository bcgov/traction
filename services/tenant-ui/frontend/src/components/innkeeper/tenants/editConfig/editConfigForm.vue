<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
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
      :disabled="loading"
    />
  </form>
</template>

<script setup lang="ts">
// Types
import { TenantConfig } from '@/types/acapyApi/acapyInterface';

// Vue
import { reactive, ref } from 'vue';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputSwitch from 'primevue/inputswitch';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';

const toast = useToast();

const emit = defineEmits(['closed', 'success']);

const { loading } = storeToRefs(useInnkeeperTenantsStore());
const innkeeperTenantsStore = useInnkeeperTenantsStore();

// Props
const props = defineProps<{
  id: string;
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

  try {
    await innkeeperTenantsStore.updateTenantConfig(props.id, {
      connect_to_endorser: [
        {
          endorser_alias: 'endorser',
          ledger_id: 'bcovrin-test',
        },
      ],
      create_public_did: ['bcovrin-test'],
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
</script>
