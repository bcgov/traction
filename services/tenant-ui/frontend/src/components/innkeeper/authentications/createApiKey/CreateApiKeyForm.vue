<template>
  <form v-if="!createdKey" @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Tenant -->
    <div class="field">
      <label
        for="selectedTenant"
        :class="{ 'p-error': v$.selectedTenant.$invalid && submitted }"
      >
        {{ $t('common.tenantName') }}
        <ProgressSpinner v-if="loading" />
      </label>

      <AutoComplete
        id="selectedTenant"
        v-model="v$.selectedTenant.$model"
        class="w-full"
        :disabled="loading"
        :suggestions="filteredTenants"
        :dropdown="true"
        option-label="label"
        force-selection
        @complete="searchTenants($event)"
      />
      <small v-if="v$.selectedTenant.$invalid && submitted" class="p-error">{{
        v$.selectedTenant.required.$message
      }}</small>
    </div>

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
      {{
        $t('apiKey.generatedKeyMessageInnkeeper', {
          key: formFields.selectedTenant.label,
        })
      }}
    </p>

    <div class="field w-8">
      <label for="">{{ $t('common.tenantId') }}</label>
      <div class="p-inputgroup">
        <InputText
          :value="formFields.selectedTenant.value"
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
  </div>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// State
import { useInnkeeperTenantsStore } from '@/store';
import { storeToRefs } from 'pinia';
// PrimeVue / Validation
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();
const innkeeperTenantsStore = useInnkeeperTenantsStore();

// use the loading state from the store to disable the button...
const { loading, tenantsDropdown } = storeToRefs(useInnkeeperTenantsStore());

// Autocomplete setup
const filteredTenants = ref();
const searchTenants = (event: any) => {
  if (!event.query.trim().length) {
    filteredTenants.value = [...(tenantsDropdown as any).value];
  } else {
    filteredTenants.value = (tenantsDropdown.value as any).filter(
      (tenant: any) => {
        return tenant.label.toLowerCase().includes(event.query.toLowerCase());
      }
    );
  }
};

// Validation
const formFields = reactive({
  selectedTenant: undefined as any,
  alias: '',
});
const rules = {
  selectedTenant: { required },
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
    const response = await innkeeperTenantsStore.createApiKey({
      tenant_id: formFields.selectedTenant.value,
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
  navigator.clipboard.writeText(formFields.selectedTenant.value);
  toast.info('Copied Tenant ID to clipboard');
};

const copyKey = () => {
  navigator.clipboard.writeText(createdKey.value);
  toast.info('Copied API Key to clipboard');
};
</script>
