<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Schema -->
    <div class="field">
      <label for="schema">Schema</label>
      <InputText
        id="schema"
        :value="schema.schema.name"
        readonly
        :disabled="loading"
        class="w-full"
      />
      <small>ID: {{ schema.schema_id }}</small>
    </div>
    <!-- Tag -->
    <div class="field">
      <label
        for="creddef_tag"
        :class="{ 'p-error': v$.creddef_tag.$invalid && submitted }"
        >Credential Definition Tag*</label
      >
      <InputText
        id="creddef_tag"
        v-model="v$.creddef_tag.$model"
        :disabled="loading"
        class="w-full"
        :class="{ 'p-invalid': v$.creddef_tag.$invalid && submitted }"
      />
      <span v-if="v$.creddef_tag.$error && submitted">
        <span v-for="(error, index) of v$.creddef_tag.$errors" :key="index">
          <small class="p-error">{{ error.$message }}</small>
        </span>
      </span>
      <small v-else-if="v$.creddef_tag.$invalid && submitted" class="p-error">{{
        v$.creddef_tag.required.$message
      }}</small>
    </div>

    <!-- Revocation -->
    <div class="field">
      <div class="field-checkbox">
        <Checkbox
          v-model="formFields.creddef_revocation_enabled"
          :disabled="loading"
          input-id="creddef_revocation_enabled"
          :binary="true"
        />
        <label for="creddef_revocation_enabled">Revocation Enabled</label>
      </div>
    </div>
    <div v-if="formFields.creddef_revocation_enabled" class="field">
      <label
        for="creddef_revocation_registry_size"
        :class="{
          'p-error': v$.creddef_revocation_registry_size.$invalid && submitted,
        }"
        >Revocation Registry Size</label
      >
      <InputText
        id="creddef_revocation_registry_size"
        v-model="v$.creddef_revocation_registry_size.$model"
        :disabled="loading"
        class="w-full"
        :class="{
          'p-invalid':
            v$.creddef_revocation_registry_size.$invalid && submitted,
        }"
      />
      <span v-if="v$.creddef_revocation_registry_size.$error && submitted">
        <span
          v-for="(error, index) of v$.creddef_revocation_registry_size.$errors"
          :key="index"
        >
          <small class="p-error">{{ error.$message }}</small>
        </span>
      </span>
    </div>

    <Button
      type="submit"
      label="Create"
      class="mt-4 w-full"
      :disabled="loading"
      :loading="loading"
    />
  </form>
</template>
<script setup lang="ts">
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';
import { reactive, ref } from 'vue';
import { useToast } from 'vue-toastification';
import { storeToRefs } from 'pinia';
import { useGovernanceStore } from '../../../store';

import { required, integer } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';

const governanceStore = useGovernanceStore();
const toast = useToast();

const props = defineProps({
  schema: {
    type: Object,
    required: true,
  },
});

// use the loading state from the store to disable the button...
const { loading, schemaTemplateDropdown, credentialDropdown } = storeToRefs(
  useGovernanceStore()
);

const emit = defineEmits(['closed', 'success']);

// const selectedSchema = computed(() => {
//   if (governanceStore.schemaTemplateDropdown != null) {
//     return (governanceStore.schemaTemplateDropdown as any).find(
//       (x: any) => x.value == props.schemaTemplateId
//     );
//   }
//   return null;
// });

// Validation
const formFields = reactive({
  creddef_tag: '',
  creddef_revocation_enabled: false,
  creddef_revocation_registry_size: '',
});

const rules = {
  creddef_tag: { required },
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

  const payload: any = {
    tag: formFields.creddef_tag,
    support_revocation: formFields.creddef_revocation_enabled,
    schema_id: props.schema.schema_id,
  };
  if (formFields.creddef_revocation_enabled) {
    let rrs = 0;
    try {
      rrs = parseInt(formFields.creddef_revocation_registry_size) || 0;
    } catch (err) {
      rrs = 0;
    }
    payload.revocation_registry_size = rrs;
  }

  try {
    // call store
    await governanceStore.createCredentialDefinition(payload);
    toast.success('Credential Definition sent to ledger');
    emit('success');
    // close on success
    emit('closed');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>
