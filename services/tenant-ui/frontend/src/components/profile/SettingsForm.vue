<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <ProgressSpinner v-if="loading" />
    <div v-else class="w-30rem">
      <!-- Wallet Label -->
      <div class="field">
        <label for="walletLabel">Wallet Label</label>
        <InputText
          id="walletLabel"
          v-model="v$.walletLabel.$model"
          class="w-full"
          :class="{ 'p-invalid': v$.walletLabel.$invalid && submitted }"
        />
        <span v-if="v$.walletLabel.$error && submitted">
          <span v-for="(error, index) of v$.walletLabel.$errors" :key="index">
            <small class="p-error">{{ error.$message }}</small>
          </span>
        </span>
      </div>

      <!-- WebHook URL -->
      <div class="webhook">
        <div class="field">
          <label
            for="webhookUrl"
            :class="{ 'p-error': v$.webhookUrl.$invalid && submitted }"
            >WebHook URL</label
          >
          <InputText
            id="webhookUrl"
            v-model="v$.webhookUrl.$model"
            class="w-full"
            :class="{ 'p-invalid': v$.webhookUrl.$invalid && submitted }"
          />
          <span v-if="v$.webhookUrl.$error && submitted">
            <span v-for="(error, index) of v$.webhookUrl.$errors" :key="index">
              <small class="p-error">{{ error.$message }}</small>
            </span>
          </span>
        </div>

        <!-- WebHook Key -->
        <div class="field">
          <label for="webhookKey">WebHook Key</label>
          <Password
            v-model="v$.webhookKey.$model"
            class="w-full"
            input-class="w-full"
            toggle-mask
            :feedback="false"
          />
        </div>
        <Button
          title="Add another webhook"
          icon="pi pi-plus-circle"
          text
          rounded
          @click="addWebhook"
        />
      </div>

      <!-- Image URL -->
      <div class="field">
        <label for="imageUrl">Image URL</label>
        <InputText id="imageUrl" v-model="v$.imageUrl.$model" class="w-full" />
      </div>

      <div>
        <Accordion>
          <AccordionTab header="Tenant Wallet Details">
            <vue-json-pretty :data="tenantWallet" />
          </AccordionTab>
        </Accordion>
      </div>
    </div>

    <Button
      class="mt-6 mb-3"
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

const toast = useToast();

// State setup
const tenantStore = useTenantStore();
const { tenantWallet, loading } = storeToRefs(useTenantStore());

const addWebhook = () => {
  console.log('addWebhook');
};

// Get Tenant Configuration
const loadTenantSettings = async () => {
  await tenantStore
    .getTenantSubWallet()
    .then(() => {
      // set the local form settings (don't bind controls directly to state for this)
      formFields.walletLabel = tenantWallet.value.settings.default_label;
      formFields.imageUrl = tenantWallet.value.settings.image_url;
      // TODO: only supporting the 1 webhook for now until some UX decisions
      // (if keeping this extract to util fxn)
      const webHookUrls = tenantWallet.value.settings['wallet.webhook_urls'];
      console.log('webHookUrls', webHookUrls);
      if (webHookUrls && webHookUrls.length) {
        // TODO: populate the formFields.webhooks array
        // TODO: loop through url array and split out the key
        // let whItem = '';
        // if (Array.isArray(webHookUrls) && typeof webHookUrls[0] === 'string') {
        //   whItem = webHookUrls[0];
        // } else if (typeof webHookUrls === 'string') {
        //   whItem = webHookUrls;
        // }
        // Split the webhook url and key
        // const pMark = whItem.indexOf('#');
        // if (pMark > 0) {
        //   formFields.webhookUrl = whItem.substring(0, whItem.indexOf('#'));
        //   formFields.webhookKey = whItem.substring(whItem.indexOf('#') + 1);
        // } else {
        //   formFields.webhookUrl = whItem;
        // }
      }
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
  webhookUrl: '',
  webhookKey: '',
  webhookds: [],
  walletLabel: '',
  imageUrl: '',
});
const rules = {
  webhookKey: {},
  webhookUrl: { url },
  walletLabel: { required },
  imageUrl: { url },
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
    const webhookUrls = [];
    if (formFields.webhookUrl) {
      let url = formFields.webhookUrl;
      if (formFields.webhookKey) {
        url += `#${formFields.webhookKey}`;
      }
      webhookUrls.push(url);
    }
    const payload = {
      image_url: formFields.imageUrl,
      label: formFields.walletLabel,
      wallet_webhook_urls: webhookUrls,
    };
    await tenantStore.updateTenantSubWallet(payload);
    loadTenantSettings();
    toast.success('Your Settings have been Updated');
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
.webhook {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  .field {
    width: 42%;
  }
  :deep(button) {
    margin-top: 20px;
  }
  :deep(button .p-button-icon) {
    font-size: 30px !important;
  }
}
</style>
