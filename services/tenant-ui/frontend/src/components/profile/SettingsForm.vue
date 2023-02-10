<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <ProgressSpinner v-if="loading" />
    <div v-else class="w-30rem">
      <!-- Wallet Label -->
      <div class="field">
        <label for="webhookKey">Wallet Label</label>
        <InputText
          id="webhookKey"
          v-model="v$.wallet_label.$model"
          class="w-full"
          :class="{ 'p-invalid': v$.wallet_label.$invalid && submitted }"
          readonly
        />
        <span v-if="v$.wallet_label.$error && submitted">
          <span v-for="(error, index) of v$.wallet_label.$errors" :key="index">
            <small class="p-error">{{ error.$message }}</small>
          </span>
        </span>
      </div>

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
        <div class="field">
          <Password
            v-model="v$.webhook_key.$model"
            class="w-full"
            input-class="w-full"
            toggle-mask
            :feedback="false"
          />
          <small v-if="v$.webhook_key.$invalid && submitted" class="p-error">
            {{ v$.webhook_key.required.$message }}
          </small>
        </div>
      </div>

      <!-- Image URL -->
      <div class="field">
        <label for="imageUrl">Image URL</label>
        <InputText id="imageUrl" v-model="v$.image_url.$model" class="w-full" />
      </div>

      <div>
        <Accordion>
          <AccordionTab header="Tenant Wallet Details">
            <vue-json-pretty :data="tenantWallet" />
          </AccordionTab>
        </Accordion>
      </div>
    </div>

    <hr class="my-4" />

    <div v-if="tenantWallet" class="grid mb-6">
      <div class="col-fixed w-8rem"><strong>Updated at</strong></div>
      <div class="col">{{ formatDateLong(tenantWallet.updated_at) }}</div>
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
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import ProgressSpinner from 'primevue/progressspinner';
import VueJsonPretty from 'vue-json-pretty';
import { useToast } from 'vue-toastification';
import { required, url } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State/etc
import { storeToRefs } from 'pinia';
import { useTenantStore } from '@/store';
import { formatDateLong } from '@/helpers';

const toast = useToast();

// State setup
const tenantStore = useTenantStore();
const { tenant, tenantWallet, loading } = storeToRefs(useTenantStore());

// Get Tenant Configuration
const loadTenantSettings = async () => {
  await tenantStore
    .getTenantSubWallet()
    .then(() => {
      // set the local form settings (don't bind controls directly to state for this)
      formFields.wallet_label = tenantWallet.value.settings.default_label;
      formFields.image_url = tenantWallet.value.settings.image_url;
      // only supporting the 1 webhook for now until some UX decisions
    })
    .catch((err: any) => {
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
  wallet_label: '',
  image_url: '',
});
const rules = {
  webhook_key: {},
  webhook_url: { url },
  wallet_label: { required },
  image_url: {},
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
