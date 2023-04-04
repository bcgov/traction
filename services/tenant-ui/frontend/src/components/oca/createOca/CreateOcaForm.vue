<template>
  <div>
    {{ formFields.selectedCred }}
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <div>
        <!-- Credential -->
        <div class="field">
          <label
            for="selectedCred"
            :class="{ 'p-error': v$.selectedCred.$invalid && submitted }"
            >Credential ID
            <ProgressSpinner v-if="loading" />
          </label>

          <AutoComplete
            id="selectedCred"
            v-model="v$.selectedCred.$model"
            class="w-full"
            :disabled="loading"
            :suggestions="filteredCreds"
            :dropdown="true"
            option-label="label"
            force-selection
            @complete="searchCreds($event)"
          />
          <small v-if="v$.selectedCred.$invalid && submitted" class="p-error">{{
            v$.selectedCred.required.$message
          }}</small>
        </div>

        <!-- Bundle URL -->
        <div class="field mt-5">
          <label
            for="bundleUrl"
            :class="{ 'p-error': v$.bundleUrl.$invalid && submitted }"
            >OCA Bundle URL*</label
          >
          <InputText
            id="bundleUrl"
            v-model="v$.bundleUrl.$model"
            class="w-full"
            :class="{ 'p-invalid': v$.bundleUrl.$invalid && submitted }"
          />
          <span v-if="v$.bundleUrl.$error && submitted">
            <span v-for="(error, index) of v$.bundleUrl.$errors" :key="index">
              <small class="p-error">{{ error.$message }}</small>
            </span>
          </span>
          <small
            v-else-if="v$.bundleUrl.$invalid && submitted"
            class="p-error"
            >{{ v$.bundleUrl.required.$message }}</small
          >
        </div>

        <Button type="submit" label="Add OCA" class="mt-5 w-full" />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// PrimeVue / Validation
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import { required, url } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { useGovernanceStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other imports
import { useToast } from 'vue-toastification';

const toast = useToast();

// Store values
const governanceStore = useGovernanceStore();
const { credentialDropdown, loading, storedCredDefs, storedSchemas } =
  storeToRefs(useGovernanceStore());

const emit = defineEmits(['closed', 'success']);

// Form / Validation setup
const filteredCreds = ref();
const formFields = reactive({
  selectedCred: undefined as any,
  bundleUrl: '',
});
const rules = {
  selectedCred: { required },
  bundleUrl: { url },
};
const v$ = useVuelidate(rules, formFields);

// Autocomplete setup
const searchCreds = (event: any) => {
  if (!event.query.trim().length) {
    filteredCreds.value = [...(credentialDropdown.value as any)];
  } else {
    filteredCreds.value = (credentialDropdown.value as any).filter(
      (cred: any) => {
        return cred.label.toLowerCase().includes(event.query.toLowerCase());
      }
    );
  }
};

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  try {
    // Get the specific schema to edit values for
    const schemaId = storedCredDefs.value.find(
      (cd: any) => cd.cred_def_id === formFields.selectedCred.value
    ).schema_id;
    const schema = storedSchemas.value.find(
      (s: any) => s.schema_id === schemaId
    );

    const payload = {
      cred_def_id: formFields.selectedCred.value,
      schema_id: schema.schema_id,
      url: formFields.bundleUrl,
    };

    // call store
    await governanceStore.createOca(payload);
    toast.info('Credential Offer Sent');
    emit('success');
    // close up on success
    emit('closed');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>
