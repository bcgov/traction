<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- DID -->
    <div class="field">
      <label for="did" :class="{ 'p-error': v$.did.$invalid && submitted }">
        {{ $t('connect.didExchange.did') }}
      </label>
      <InputText
        id="did"
        v-model="v$.did.$model"
        class="w-full"
        :class="{ 'p-invalid': v$.did.$invalid && submitted }"
      />
      <small v-if="v$.did.$invalid && submitted" class="p-error"
        >{{ v$.did.required.$message }}
      </small>
    </div>

    <!-- Alias -->
    <div class="field">
      <label for="alias" :class="{ 'p-error': v$.alias.$invalid && submitted }">
        {{ $t('common.alias') }}
      </label>
      <InputText
        id="alias"
        v-model="v$.alias.$model"
        class="w-full"
        :class="{ 'p-invalid': v$.alias.$invalid && submitted }"
      />
      <span v-if="v$.alias.$error && submitted">
        <span v-for="(error, index) of v$.alias.$errors" :key="index">
          <small class="p-error">{{ error.$message }}</small>
        </span>
      </span>
      <small v-else-if="v$.alias.$invalid && submitted" class="p-error"
        >{{ v$.alias.required.$message }}
      </small>
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
import { useConnectionStore, useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { maxLength, required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';

const toast = useToast();
const connectionStore = useConnectionStore();

// use the loading state from the store to disable the button...
const { loading } = storeToRefs(useConnectionStore());
// Tenant details for my_label
const { tenant } = storeToRefs(useTenantStore());

const emit = defineEmits(['closed', 'success']);

// Validation
const formFields = reactive({
  did: '',
  alias: '',
});
const rules = {
  did: { required },
  alias: { required, maxLengthValue: maxLength(255) },
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
    await connectionStore.didCreateRequest(
      formFields.did,
      formFields.alias,
      tenant.value.tenant_name
    );
    emit('success');
    // close up on success
    emit('closed');
    toast.info('DID Exchange request sent');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>
