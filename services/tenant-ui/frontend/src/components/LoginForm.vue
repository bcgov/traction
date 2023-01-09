<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <div class="field mt-5 w-full">
      <!-- ID -->
      <label
        for="wallet-id"
        :class="{ 'p-error': v$.walletId.$invalid && submitted }"
        >Wallet ID
      </label>
      <InputText
        id="wallet-id"
        v-model="v$.walletId.$model"
        type="text"
        option-label="label"
        autocomplete="username"
        name="username"
        autofocus
        class="w-full"
      />
      <small v-if="v$.walletId.$invalid && submitted" class="p-error">{{
        v$.walletId.required.$message
      }}</small>
    </div>

    <div class="field mt-5 w-full">
      <!-- Secret -->
      <label
        for="wallet-id"
        :class="{ 'p-error': v$.walletSecret.$invalid && submitted }"
        >Wallet Secret
      </label>
      <InputText
        id="wallet-secret"
        v-model="v$.walletSecret.$model"
        type="password"
        autocomplete="current-password"
        name="walletsecret"
        class="w-full"
      />
      <small v-if="v$.walletSecret.$invalid && submitted" class="p-error">{{
        v$.walletSecret.required.$message
      }}</small>

      <Button
        type="submit"
        class="w-full mt-5"
        label="Sign-In"
        :disabled="!!loading"
        :loading="!!loading"
      />
    </div>

    <!-- Delme for testing only -->
    <div class="field mt-5 w-full">
      <label for="wallet-id">Wallet ID</label>
      <div class="p-inputgroup">
        <InputText id="wallet-id" readonly name="wallet-id" class="w-full" />
        <Button
          icon="pi pi-copy"
          class="p-button-secondary"
          title="Copy to clipboard"
        />
      </div>
    </div>
    <!---------------------------->
  </form>
</template>

<script setup lang="ts">
//Vue
import { ref, reactive } from 'vue';
// PrimeVue/Validation/etc
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { useTenantStore, useTokenStore } from '../store';
import { storeToRefs } from 'pinia';

const toast = useToast();

// Login Form and validation
const formFields = reactive({
  walletId: '',
  walletSecret: '',
});
const rules = {
  walletId: { required },
  walletSecret: { required },
};
const v$ = useVuelidate(rules, formFields);

// State setup
const tokenStore = useTokenStore();
// use the loading state from the store to disable the button...
const { loading, token } = storeToRefs(useTokenStore());
const tenantStore = useTenantStore();
const { tenant } = storeToRefs(useTenantStore());

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  try {
    await tokenStore.login(formFields.walletId, formFields.walletSecret);
    console.log(token.value);
  } catch (err) {
    console.error(err);
    toast.error(`Failure getting token: ${err}`);
  }
  try {
    // token is loaded, now go fetch the tenant data...
    // await tenantStore.getSelf();
    console.log(tenant.value);
  } catch (err) {
    console.error(err);
    toast.error(`Failure getting tenant: ${err}`);
  } finally {
    submitted.value = false;
  }
};
</script>

<style>
.field .p-inputgroup .p-inputtext {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
.field .p-inputgroup button.p-button {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
</style>
