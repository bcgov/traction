<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <ProgressSpinner v-if="loading" />
    <div v-else class="settings-form">
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

      <!-- Webhooks -->

      <Divider class="websockets-top" align="left" type="solid">
        <b>Webhooks</b>
      </Divider>

      <div class="webhooks">
        <TransitionGroup appear name="wh">
          <div
            class="webhook"
            v-for="(webhook, index) of formFields.webhooks"
            :key="index"
          >
            <div class="field">
              <label for="webhookUrl">WebHook URL</label>
              <InputText
                id="webhookUrl"
                v-model="webhook.webhookUrl"
                class="w-full"
              />
            </div>

            <div class="field">
              <label for="webhookKey">WebHook Key</label>
              <Password
                id="webhookKey"
                v-model="webhook.webhookKey"
                class="w-full"
                toggle-mask
                :feedback="false"
              />
            </div>

            <Button
              title="Delete this webhook"
              icon="pi pi-trash"
              text
              rounded
              @click="() => removeWebhook(index)"
            />

            <Button
              title="Add another webhook"
              class="add"
              icon="pi pi-plus-circle"
              text
              rounded
              @click="addWebhook"
            />
          </div>
        </TransitionGroup>
      </div>

      <Divider class="websockets-bottom" />

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
import { onMounted, reactive, ref, Transition, TransitionGroup } from 'vue';
// PrimeVue/Validation
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Button from 'primevue/button';
import Divider from 'primevue/divider';
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

// Get Tenant Configuration
const loadTenantSettings = async () => {
  await tenantStore
    .getTenantSubWallet()
    .then(() => {
      // set the local form settings (don't bind controls directly to state for this)
      formFields.walletLabel = tenantWallet.value.settings.default_label;
      formFields.imageUrl = tenantWallet.value.settings.image_url;

      const webHookUrls = tenantWallet.value.settings['wallet.webhook_urls'];

      // Clear the webhook array if necessary
      if (formFields.webhooks.length > 0) {
        formFields.webhooks = [];
      }

      if (webHookUrls && webHookUrls.length) {
        webHookUrls.forEach((whItem: string) => {
          const pMark = whItem.indexOf('#');
          if (pMark > 0) {
            const webhookUrl = whItem.substring(0, whItem.indexOf('#'));
            const webhookKey = whItem.substring(whItem.indexOf('#') + 1);
            formFields.webhooks.push({
              webhookUrl,
              webhookKey,
            });
          }
        });
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
  webhooks: [{ webhookUrl: '', webhookKey: '' }],
  walletLabel: '',
  imageUrl: '',
});
const rules = {
  webhooks: {
    $each: {
      webhookKey: {},
      webhookUrl: { url },
    },
  },
  walletLabel: { required },
  imageUrl: { url },
};
const v$ = useVuelidate(rules, formFields);

/**
 * Add a blank webhook entry
 */
const addWebhook = () => {
  formFields.webhooks.push({ webhookUrl: '', webhookKey: '' });
};

/**
 * Remove a webhook but don't allow the last one to be removed.
 * Just blank it out.
 */
const removeWebhook = (index: number) => {
  formFields.webhooks.splice(index, 1);

  // If this is the last entry in the array, add a new blank one.
  if (formFields.webhooks.length === 0) addWebhook();
};

// Submitting form
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }

  try {
    const webhooks: Array<string> = [];
    if (formFields.webhooks && formFields.webhooks.length) {
      formFields.webhooks.forEach((whItem: any) => {
        let url = whItem.webhookUrl;
        if (whItem.webhookKey) {
          url += `#${whItem.webhookKey}`;
        }
        webhooks.push(url);
      });
    }
    const payload = {
      image_url: formFields.imageUrl,
      label: formFields.walletLabel,
      wallet_webhook_urls: webhooks,
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
.settings-form {
  width: 40rem !important;
}
.webhook {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  .field {
    width: 41%;
  }
  :deep(button) {
    margin-top: 20px;
  }
  :deep(button .p-button-icon) {
    font-size: 30px !important;
  }
  button.add {
    visibility: hidden;
  }
}
/* Show the add button on the last webhook */
.webhooks div:last-of-type {
  button.add {
    visibility: visible;
  }
}
.websockets-bottom {
  margin-top: 0px !important;
}
.websockets-top {
  margin-bottom: 5px !important;
}

.wh-enter-active,
.wh-leave-active {
  transition: opacity 0.5s ease;
}
.wh-enter-from,
.wh-leave-to {
  opacity: 0;
}
</style>
