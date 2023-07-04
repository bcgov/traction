<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <div class="field mt-5 w-full">
      <!-- ID -->
      <label
        for="wallet-id"
        :class="{ 'p-error': v$.walletId.$invalid && submitted }"
      >
        {{ $t('common.walletId') }}
      </label>
      <InputText
        id="wallet-id"
        v-model="v$.walletId.$model"
        type="text"
        option-label="label"
        autocomplete="wallet-id"
        name="walledId"
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
        for="wallet-secret"
        :class="{ 'p-error': v$.walletSecret.$invalid && submitted }"
      >
        {{ $t('login.walletSecret') }}
      </label>
      <InputText
        id="wallet-secret"
        v-model="v$.walletSecret.$model"
        type="password"
        option-label="label"
        autocomplete="wallet-secret"
        name="walletSecret"
        class="w-full"
      />
      <small v-if="v$.walletSecret.$invalid && submitted" class="p-error">{{
        v$.walletSecret.required.$message
      }}</small>

      <Button
        type="submit"
        class="w-full mt-5"
        :label="$t('login.submit')"
        :disabled="!!loading"
        :loading="!!loading"
      />

      <Message v-if="invalidCreds" severity="error" :closable="false">
        {{ $t('login.invalidCreds') }}
      </Message>
    </div>
  </form>
</template>

<script setup lang="ts">
//Vue
import { ref, reactive } from 'vue';
// PrimeVue/Validation/etc
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';
import { useToast } from 'vue-toastification';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { useTenantStore, useTokenStore } from '../store';
import { storeToRefs } from 'pinia';

const toast = useToast();

// Login Form and validation
const invalidCreds = ref(false);
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

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  invalidCreds.value = false;
  submitted.value = true;

  if (!isFormValid) {
    return;
  }

  // Use the wallet creds to get a token
  try {
    // Trim wallet ID and wallet key
    formFields.walletId = formFields.walletId.trim();
    formFields.walletSecret = formFields.walletSecret.trim();

    // Get a token
    await tokenStore.login(formFields.walletId, formFields.walletSecret);
    console.log(token.value);
  } catch (err: any) {
    console.error(err);
    if (err.response?.status === 404 || err.response?.status === 409) {
      // Handle wallet not found or bad password for this as a status not an exception
      invalidCreds.value = true;
    } else {
      toast.error(`Failure getting token: ${err}`);
    }
  }

  // token is loaded, now go fetch the global data about the tenant
  if (token.value) {
    try {
      const results = await Promise.allSettled([
        tenantStore.getSelf(),
        tenantStore.getTenantConfig(),
        tenantStore.getIssuanceStatus(),
      ]);
      // if any the Tenant details fetch fails, throw the first error
      results.forEach((result) => {
        if (result.status === 'rejected') {
          throw result.reason;
        }
      });
    } catch (err) {
      console.error(err);
      toast.error(`Failure getting tenant info: ${err}`);
    } finally {
      submitted.value = false;
    }
  }
};
</script>
