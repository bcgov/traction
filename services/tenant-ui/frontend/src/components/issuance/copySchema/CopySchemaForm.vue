<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <!-- Main Form -->
      <div>
        <div class="field mt-5">
          <label
            for="schemaId"
            :class="{ 'p-error': v$.schemaId.$invalid && submitted }"
            >Schema Id*</label
          >
          <InputText
            id="schemaId"
            v-model="v$.schemaId.$model"
            :class="{ 'p-invalid': v$.schemaId.$invalid && submitted }"
          />
          <span v-if="v$.schemaId.$error && submitted">
            <span v-for="(error, index) of v$.schemaId.$errors" :key="index">
              <small class="p-error">{{ error.$message }}</small>
            </span>
          </span>
          <small
            v-else-if="v$.schemaId.$invalid && submitted"
            class="p-error"
            >{{ v$.schemaId.required.$message }}</small
          >
        </div>
        <Button type="submit" label="Copy Schema" class="mt-5 w-full" />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { useGovernanceStore } from '@/store';
// Other imports
import { useToast } from 'vue-toastification';

const toast = useToast();

// Store values
const governanceStore = useGovernanceStore();

// Form / Validation setup
const formFields = reactive({
  schemaId: '',
});
const rules = {
  schemaId: { required },
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
    const payload = {
      schema_id: formFields.schemaId,
      name: null,
      tags: [],
    };

    // call store
    await governanceStore.copySchema(payload);
    toast.info('Schema copied');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>

<style>
/* TODO: app-wide style (like form layout) to go in a global scss */
.field > label,
.field > small.p-error {
  display: block !important;
}
</style>
