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
    <p>
      {{ $t('apiKey.generatedKey') }} <br />
      <strong>{{ createdKey }}</strong>
    </p>
  </div>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// State
import { useKeyManagementStore } from '@/store';
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
const { loading } = storeToRefs(useKeyManagementStore());

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
</script>
