<template>
  <ProgressSpinner v-if="loading" />
  <div v-else class="w-30rem">
    <!-- WebHook URL -->
    <div class="field">
      <label for="webhookUrl">WebHook URL</label>
      <InputText id="webhookUrl" class="w-full" />
    </div>
    <!-- WebHook Key -->
    <div class="field">
      <label for="webhookKey">WebHook Key</label>
      <InputText id="webhookKey" class="w-full" />
    </div>
    <!-- Auto Respond -->
    <p class="mb-1">Auto Respond Messages</p>
    <InputSwitch />
    <!-- Message -->
    <div class="field mt-2">
      <label for="autoResMessage">Auto Response Message</label>
      <Textarea id="autoResMessage" rows="5" class="w-full" />
    </div>
    <!-- Store Messages -->
    <p class="mb-1">Store Messages</p>
    <InputSwitch />
    <!-- Store creds -->
    <p class="mb-1">Store Issuer Credentials</p>
    <InputSwitch />
  </div>

  <hr class="my-4" />

  <div v-if="tenantConfig" class="grid mb-6">
    <div class="col-fixed w-8rem"><strong>Updated at</strong></div>
    <div class="col">{{ formatDateLong(tenantConfig.updated_at) }}</div>
  </div>

  <Button :disabled="loading" label="Save Changes" />
</template>

<script setup lang="ts">
// Vue
import { onMounted, reactive } from 'vue';
// PrimeVue/Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputSwitch from 'primevue/inputswitch';
import ProgressSpinner from 'primevue/progressspinner';
import Textarea from 'primevue/textarea';
import { useToast } from 'vue-toastification';
import { maxLength, required, url } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State/etc
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';
import { formatDateLong } from '@/helpers';

const toast = useToast();

// State setup
const tenantStore = useTenantStore();
const { tenantConfig, loading } = storeToRefs(useTenantStore());

// Get Tenant Configuration
const loadTenantSettings = async () => {
  tenantStore.getConfiguration().catch((err: any) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
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
  webhook_key: { url },
  webhook_url: { url },
  auto_respond_messages: {},
  auto_response_message: {},
  store_messages: {},
  store_issuer_credentials: {},
};
const v$ = useVuelidate(rules, formFields);
</script>

<style scoped lang="scss">
hr {
  height: 1px;
  background-color: rgb(186, 186, 186);
  border: 0;
}
</style>
