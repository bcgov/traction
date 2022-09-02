<template>
  <h3 class="mt-0 mb-5">Create Credential Template</h3>
  <div class="form-demo">
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <!-- Schema -->
      <div class="field">
        <div class="p-float-label">
          <InputText
            id="schema"
            v-model="selectedSchema.label"
            :readonly="true"
          />
          <label for="schema">Schema*</label>
        </div>
      </div>
      <!-- Name -->
      <div class="field">
        <div class="p-float-label">
          <InputText
            id="name"
            v-model="v$.name.$model"
            :class="{ 'p-invalid': v$.name.$invalid && submitted }"
          />
          <label
            for="name"
            :class="{ 'p-error': v$.name.$invalid && submitted }"
            >Name*</label
          >
        </div>
        <span v-if="v$.name.$error && submitted">
          <span v-for="(error, index) of v$.name.$errors" :key="index">
            <small class="p-error">{{ error.$message }}</small>
          </span>
        </span>
        <small v-else-if="v$.name.$invalid && submitted" class="p-error">{{
          v$.name.required.$message
        }}</small>
      </div>
      <!-- Tag -->
      <div class="field">
        <div class="p-float-label">
          <InputText
            id="creddef_tag"
            v-model="v$.creddef_tag.$model"
            :class="{ 'p-invalid': v$.creddef_tag.$invalid && submitted }"
          />
          <label
            for="creddef_tag"
            :class="{ 'p-error': v$.creddef_tag.$invalid && submitted }"
            >Credential Definition Tag*</label
          >
        </div>
        <span v-if="v$.creddef_tag.$error && submitted">
          <span v-for="(error, index) of v$.creddef_tag.$errors" :key="index">
            <small class="p-error">{{ error.$message }}</small>
          </span>
        </span>
        <small
          v-else-if="v$.creddef_tag.$invalid && submitted"
          class="p-error"
          >{{ v$.creddef_tag.required.$message }}</small
        >
      </div>

      <!-- Revocation -->
      <div class="field">
        <div class="field-checkbox">
          <Checkbox
            v-model="formFields.creddef_revocation_enabled"
            input-id="creddef_revocation_enabled"
            :binary="true"
          />
          <label for="creddef_revocation_enabled">Revocation Enabled</label>
        </div>
      </div>
      <div class="field">
        <div class="p-float-label">
          <InputText
            id="creddef_revocation_registry_size"
            v-model="v$.creddef_revocation_registry_size.$model"
            :class="{
              'p-invalid':
                v$.creddef_revocation_registry_size.$invalid && submitted,
            }"
          />
          <label
            for="creddef_revocation_registry_size"
            :class="{
              'p-error':
                v$.creddef_revocation_registry_size.$invalid && submitted,
            }"
            >Revocation Registry Size</label
          >
        </div>
        <span v-if="v$.creddef_revocation_registry_size.$error && submitted">
          <span
            v-for="(error, index) of v$.creddef_revocation_registry_size
              .$errors"
            :key="index"
          >
            <small class="p-error">{{ error.$message }}</small>
          </span>
        </span>
      </div>

      <Button
        type="submit"
        label="Create"
        class="mt-1"
        :disabled="loading"
        :loading="loading"
      />
    </form>
  </div>
</template>
<script setup lang="ts">
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';
import { computed, reactive, ref } from 'vue';
import { useToast } from 'vue-toastification';
import { storeToRefs } from 'pinia';
import { useGovernanceStore } from '../../../store';

import { required, integer } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';

const governanceStore = useGovernanceStore();
const toast = useToast();

const props = defineProps({
  schemaTemplateId: {
    type: String,
    required: true,
  },
});

// use the loading state from the store to disable the button...
const { loading, schemaTemplateDropdown, credentialTemplateDropdown } =
  storeToRefs(useGovernanceStore());

const selectedSchema = computed(() => {
  if (governanceStore.schemaTemplateDropdown != null) {
    return governanceStore.schemaTemplateDropdown.find(
      (x) => x.value == props.schemaTemplateId
    );
  }
  return null;
});

// Validation
const formFields = reactive({
  name: '',
  creddef_tag: '',
  creddef_revocation_enabled: false,
  creddef_revocation_registry_size: '',
});

const rules = {
  creddef_tag: { required },
  name: { required },
  creddef_revocation_registry_size: { integer },
};
const v$ = useVuelidate(rules, formFields);

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }

  let rrs = 0;
  try {
    rrs = parseInt(formFields.creddef_revocation_registry_size) || 0;
  } catch (err) {
    rrs = 0;
  }
  const payload = {
    credential_definition: {
      tag: formFields.creddef_tag,
      revocation_enabled: formFields.creddef_revocation_enabled,
      revocation_registry_size: rrs,
    },
    schema_template_id: props.schemaTemplateId,
    name: formFields.name,
    tags: [],
  };

  console.log(payload);

  try {
    // call store
    await governanceStore.createCredentialTemplate(payload);
    toast.info('Credential Template Created');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>
