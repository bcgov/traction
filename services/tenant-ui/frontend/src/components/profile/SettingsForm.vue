<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <ProgressSpinner v-if="loading" />
    <div v-else class="w-30rem">
      <!-- WebHook URL -->
      <div class="field">
        <label
          for="webhookUrl"
          :class="{ 'p-error': v$.webhook_url.$invalid && submitted }"
          >WebHook URL</label
        >
        <InputText
          id="webhookUrl"
          v-model="v$.webhook_url.$model"
          class="w-full"
          :class="{ 'p-invalid': v$.webhook_url.$invalid && submitted }"
        />
        <span v-if="v$.webhook_url.$error && submitted">
          <span v-for="(error, index) of v$.webhook_url.$errors" :key="index">
            <small class="p-error">{{ error.$message }}</small>
          </span>
        </span>
      </div>
      <!-- WebHook Key -->
      <div class="field">
        <label for="webhookKey">WebHook Key</label>
        <InputText
          id="webhookKey"
          v-model="v$.webhook_key.$model"
          class="w-full"
        />
      </div>
      <!-- Auto Respond -->
      <p class="mb-1">Auto Respond Messages</p>
      <InputSwitch v-model="v$.auto_respond_messages.$model" />
      <!-- Message -->
      <div v-if="v$.auto_respond_messages.$model" class="field mt-2">
        <label for="autoResMessage">Auto Response Message</label>
        <Textarea
          id="autoResMessage"
          v-model="v$.auto_response_message.$model"
          rows="3"
          class="w-full"
        />
      </div>

      <div>
        <i class="pi pi-info-circle ml-0" />
        <span>Can only set fields below if you have Innkeeper approval</span>
      </div>
      <!-- Store Messages -->
      <p class="my-1">Store Messages</p>
      <InputSwitch v-model="v$.store_messages.$model" />
      <!-- Store creds -->
      <p class="mb-1">Store Issuer Credentials</p>
      <InputSwitch v-model="v$.store_issuer_credentials.$model" />
    </div>

    <hr class="my-4" />

    <div v-if="tenantConfig" class="grid mb-6">
      <div class="col-fixed w-8rem"><strong>Updated at</strong></div>
      <div class="col">{{ formatDateLong(tenantConfig.updated_at) }}</div>
    </div>

    <Button
      :disabled="loading"
      :loading="loading"
      label="Save Changes"
      type="submit"
    />
  </form>
</template>

<script setup lang="ts">
// Vue
import { onMounted, reactive, ref } from 'vue';
// PrimeVue/Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputSwitch from 'primevue/inputswitch';
import ProgressSpinner from 'primevue/progressspinner';
import Textarea from 'primevue/textarea';
import { useToast } from 'vue-toastification';
import { maxLength, url } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State/etc
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';
import { formatDateLong } from '@/helpers';

const toast = useToast();

// State setup
const tenantStore = useTenantStore();
const { tenant, tenantConfig, loading } = storeToRefs(useTenantStore());

// Get Tenant Configuration
const loadTenantSettings = async () => {
  // await tenantStore
  //   .getConfiguration()
  //   .then(() => {
  //     // set the local form settings (don't bind controls directly to state for this)
  //     Object.assign(formFields, tenantConfig.value);
  //     // Set the 'default' if nothing there to show the user the default auto-response
  //     if (!formFields.auto_response_message) {
  //       formFields.auto_response_message = `'${tenant.value.name}' has recieved your message but does not correspond via messages`;
  //     }
  //   })
  //   .catch((err: any) => {
  //     console.error(err);
  //     toast.error(`Failure: ${err}`);
  //   });
};
onMounted(async () => {
  loadTenantSettings();
});

// Form Fields and Validation
const formFields = reactive({
  webhook_url: '',
  webhook_key: '',
  auto_respond_messages: false,
  auto_response_message: '',
  store_messages: false,
  store_issuer_credentials: false,
});
const rules = {
  webhook_key: {},
  webhook_url: { url },
  auto_respond_messages: {},
  auto_response_message: { maxLengthValue: maxLength(255) },
  store_messages: {},
  store_issuer_credentials: {},
};
const v$ = useVuelidate(rules, formFields);

// Submitting form
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }

  try {
    // await tenantStore.updateConfiguration(formFields);
    // toast.info('Your Settings have been Updated');
    toast.error('unimplimented');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>

<style scoped lang="scss">
hr {
  height: 1px;
  background-color: rgb(186, 186, 186);
  border: 0;
}
</style>
