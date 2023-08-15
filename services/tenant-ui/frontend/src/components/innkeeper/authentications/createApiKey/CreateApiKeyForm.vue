<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Tenant -->
    <div class="field">
      <label
        for="tenantId"
        :class="{ 'p-error': v$.tenantId.$invalid && submitted }"
      >
        Tenant ID
      </label>
      <InputText
        id="tenantId"
        v-model="v$.tenantId.$model"
        class="w-full"
        :class="{ 'p-invalid': v$.tenantId.$invalid && submitted }"
      />
      <small v-if="v$.tenantId.$invalid && submitted" class="p-error"
        >{{ v$.tenantId.required.$message }}
      </small>
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
    </div>
    <Button
      type="submit"
      :label="$t('common.submit')"
      class="mt-5 w-full"
      :disabled="loading"
      :loading="loading"
    />
  </form>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// State
import { useInnkeeperTenantsStore } from '@/store';
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
const innkeeperTenantsStore = useInnkeeperTenantsStore();

// use the loading state from the store to disable the button...
const { loading } = storeToRefs(useInnkeeperTenantsStore());

const emit = defineEmits(['closed', 'success']);

// Validation
const formFields = reactive({
  tenantId: '',
  alias: '',
});
const rules = {
  tenantId: { required },
  alias: {},
};
const v$ = useVuelidate(rules, formFields);

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }

  try {
    await innkeeperTenantsStore.createApiKey({
      tenant_id: formFields.tenantId,
      alias: formFields.alias,
    });
    emit('success');
    // close up on success
    emit('closed');
    toast.info(t('apiKey.createSuccess'));
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>
