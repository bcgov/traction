<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Form to create tenant -->
    <div v-if="!checkinResponse">
      <!-- Name -->
      <div class="field">
        <label
          for="tenantName"
          :class="{ 'p-error': v$.name.$invalid && submitted }"
        >
          Tenant Name
        </label>
        <InputText
          v-model="v$.name.$model"
          :class="{ 'p-invalid': v$.name.$invalid && submitted }"
          type="text"
          name="tenantName"
          autofocus
          :disabled="loading"
        />
        <small v-if="v$.name.$invalid && submitted" class="p-error"
          >{{ v$.name.required.$message }}
        </small>
      </div>

      <!-- Make Issuer -->
      <p class="mb-1 mt-5">Allow Tenant to make themselves an issuer</p>
      <InputSwitch v-model="v$.allowIssue.$model" :disabled="loading" />

      <Button
        type="submit"
        label="Check-In"
        class="mt-6 w-full"
        :loading="loading"
      />
    </div>

    <!-- Show the wallet ID and key after check in  -->
    <div v-else>
      <div class="wallet-key-text">
        <i class="pi pi-exclamation-triangle" />
        <span>
          Please <strong>securely</strong> provide the following credentials to
          the Tenant manager. <br />
          Note that you will <strong>not</strong>
          be able to access the key again after closing this.
        </span>
      </div>

      <Panel header="Wallet Access for Tenant">
        <template #icons>
          <Button
            label="Copy to Clipboard"
            class="p-button-text"
            @click="copy_to_clipboard()"
          />
        </template>
        <p>Wallet ID: {{ checkinResponse.wallet_id }}</p>

        <p>Wallet Key: {{ checkinResponse.wallet_key }}</p>
      </Panel>

      <Button label="Close" class="mt-5 w-full" @click="closeForm" />
    </div>
  </form>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// State
import { useInnkeeperTenantsStore } from '@/store';
import type { TenantResponseData } from '@/store/innkeeper/innkeeperTenantsStore';
import { storeToRefs } from 'pinia';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputSwitch from 'primevue/inputswitch';
import Panel from 'primevue/panel';
import { useConfirm } from 'primevue/useconfirm';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';

// state
const innkeeperTenantsStore = useInnkeeperTenantsStore();
const { loading } = storeToRefs(useInnkeeperTenantsStore());

const toast = useToast();
const confirm = useConfirm();

// To store local data
const checkinResponse = ref<TenantResponseData | null>(null);

const emit = defineEmits(['closed', 'success']);

// Validation
const formFields = reactive({
  name: '',
  allowIssue: false,
});
const rules = {
  name: { required },
  allowIssue: {},
};
const v$ = useVuelidate(rules, formFields);

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean): Promise<void> => {
  submitted.value = true;
  if (!isFormValid) {
    return;
  }
  try {
    const data = {
      name: formFields.name,
      allowIssue: formFields.allowIssue,
    };
    // call store
    const result = await innkeeperTenantsStore.checkInTenant(data);
    if (result != null) {
      checkinResponse.value = result;
      toast.success(`Tenant ${formFields.name} Checked In Successfully`);
      emit('success');
    }
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};

// Copying key to clipboard
const copy_to_clipboard = (): void => {
  navigator.clipboard.writeText(`Wallet ID: ${checkinResponse.value?.wallet_id}
  \r\nWallet Key: ${checkinResponse.value?.wallet_key}`);
  toast.info('Wallet information copied to clipboard');
};

// Close the form after check in
// Parent will not let the form close by other avenues once checked-in
const closeForm = (event: any): void => {
  confirm.require({
    target: event.target,
    message:
      'Are you sure? You will not be able to retrieve this wallet key again after this.',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      emit('closed');
    },
  });
};
</script>

<style lang="scss" scoped>
.wallet-key-text {
  display: flex;
  margin-bottom: 2em;
  .pi {
    margin: 0.2em 0.7em 0 0;
    font-size: 1.8em;
  }
}
</style>
