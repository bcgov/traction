<template>
  <form v-if="!createdKey" @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Alias -->
    <div class="field">
      <label for="alias" :class="{ 'p-error': v$.alias.$invalid && submitted }">
        {{ $t('apiKey.alias') }}
      </label>
      <InputText
        id="alias"
        v-model="v$.alias.$model"
        class="w-full"
        :class="{ 'p-invalid': v$.alias.$invalid && submitted }"
      />
      <small v-if="v$.alias.$invalid && submitted" class="p-error">{{
        v$.alias.required.$message
      }}</small>
    </div>
    <Button
      type="submit"
      :label="$t('common.submit')"
      class="mt-5 w-full"
      :disabled="loading"
      :loading="loading"
    />
  </form>
  <!-- Display created key the one time -->
  <div v-else>
    <p>
      {{ $t('apiKey.generatedKeyMessage') }}
    </p>

    <div class="field w-8">
      <label for="">{{ $t('common.tenantId') }}</label>
      <div class="p-inputgroup">
        <InputText
          :value="tenant.tenant_id"
          type="text"
          readonly
          class="w-full"
        />
        <Button
          icon="pi pi-copy"
          title="Copy to clipboard"
          class="p-button-secondary"
          @click="copyTenantId"
        />
      </div>
    </div>

    <p>
      {{ $t('apiKey.generatedKey') }}
    </p>

    <div class="field w-8">
      <label for="">{{ $t('common.apiKey') }}</label>
      <div class="p-inputgroup">
        <InputText :value="createdKey" type="text" readonly class="w-full" />
        <Button
          icon="pi pi-copy"
          title="Copy to clipboard"
          class="p-button-secondary"
          @click="copyKey"
        />
      </div>
    </div>

    <i class="pi pi-info-circle mt-4" style="font-size: 1.5rem" />
    <p class="mt-0">
      {{ $t('apiKey.docs') }} <br />
      {{ $t('apiKey.docsSwagger') }} <br />
      <a :href="swaggerUrl" target="_blank">
        <small> {{ swaggerUrl }}</small>
        <i class="pi pi-external-link ml-2" />
      </a>
    </p>
  </div>
</template>

<script setup lang="ts">
// Vue
import { computed, reactive, ref } from 'vue';
// State
import { useConfigStore, useKeyManagementStore, useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();
const keyManagementStore = useKeyManagementStore();

// use the loading state from the store to disable the button...
const { config } = storeToRefs(useConfigStore());
const { loading } = storeToRefs(useKeyManagementStore());
const { tenant } = storeToRefs(useTenantStore());

// Validation
const formFields = reactive({
  alias: '',
});
const rules = {
  alias: { required },
};
const v$ = useVuelidate(rules, formFields);

// Form submission
const createdKey = ref('');
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }

  try {
    const response = await keyManagementStore.createApiKey({
      alias: formFields.alias,
    });
    createdKey.value = response?.api_key || '';
    toast.success(t('apiKey.createSuccess'));
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};

// Copy to clipboard
const copyTenantId = () => {
  navigator.clipboard.writeText(tenant.value.tenant_id);
  toast.info('Copied Tenant ID to clipboard');
};

const copyKey = () => {
  navigator.clipboard.writeText(createdKey.value);
  toast.info('Copied API Key to clipboard');
};

// Swagger link
const swaggerUrl = computed(
  () =>
    `${config.value.frontend.tenantProxyPath}/api/doc#/multitenancy/post_multitenancy_tenant__tenant_id__token`
);
</script>
