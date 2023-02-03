<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <!-- Main Form -->
      <div>
        <!-- schema name -->
        <div class="field mt-5">
          <label
            for="schemaName"
            :class="{ 'p-error': v$.schemaName.$invalid && submitted }"
            >Schema Name*</label
          >
          <InputText
            id="schemaName"
            v-model="v$.schemaName.$model"
            class="w-full"
            :class="{ 'p-invalid': v$.schemaName.$invalid && submitted }"
          />
          <span v-if="v$.schemaName.$error && submitted">
            <span v-for="(error, index) of v$.schemaName.$errors" :key="index">
              <small class="p-error">{{ error.$message }}</small>
            </span>
          </span>
          <small
            v-else-if="v$.schemaName.$invalid && submitted"
            class="p-error"
            >{{ v$.schemaName.required.$message }}</small
          >
        </div>
        <!-- schema version -->
        <div class="field mt-5">
          <label
            for="schemaVersion"
            :class="{ 'p-error': v$.schemaVersion.$invalid && submitted }"
            >Schema Version*</label
          >
          <InputText
            id="schemaVersion"
            v-model="v$.schemaVersion.$model"
            class="w-full"
            :class="{ 'p-invalid': v$.schemaVersion.$invalid && submitted }"
          />
          <span v-if="v$.schemaVersion.$error && submitted">
            <span
              v-for="(error, index) of v$.schemaVersion.$errors"
              :key="index"
            >
              <small class="p-error">{{ error.$message }}</small>
            </span>
          </span>
          <small
            v-else-if="v$.schemaVersion.$invalid && submitted"
            class="p-error"
            >{{ v$.schemaVersion.required.$message }}</small
          >
        </div>
        <!-- attributes -->
        <h4 style="margin-bottom: 0.5rem; font-weight: normal">Attributes*</h4>
        <div
          v-for="(item, index) in attributes"
          :key="index"
          class="flex w-full"
        >
          <InputText
            v-model="item.name"
            type="text"
            name="{{ `attribute_${index}` }}"
            class="mb-5 w-full"
          />
          <div class="flex justify-content-between">
            <button
              class="ml-1 p-button p-component p-button-icon-only p-button-rounded p-button-danger p-button-text p-float-left"
              type="button"
              @click="removeAttribute(index)"
            >
              <span class="pi pi-times p-button-icon"></span>
            </button>
            <button
              v-if="index === 0"
              class="ml-1 p-button p-component p-button-icon-only p-button-rounded p-button-outlined"
              type="button"
              @click="addAttribute"
            >
              <span class="pi pi-plus p-button-icon"></span>
            </button>
          </div>
        </div>
        <Button type="submit" label="Create Schema" class="mt-5 w-full" />
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
import { required, helpers } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { useGovernanceStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other imports
import { useToast } from 'vue-toastification';

const toast = useToast();

// Store values
const governanceStore = useGovernanceStore();
const { loading } = storeToRefs(useGovernanceStore());

const emit = defineEmits(['closed', 'success']);

const addAttribute = () => {
  attributes.value.push({ name: '', type: '' });
};

/**
 * ## removeAttribute
 * Remove an attribute from the schema.
 */
const removeAttribute = (index: number) => {
  if (attributes.value.length > 1) {
    attributes.value.splice(index, 1);
  }
};

// Store an array of attributes. Start with an empty attribute
const attributes = ref([{ name: '', type: '' }]);

// Form / Validation setup
const formFields = reactive({
  schemaName: '',
  schemaVersion: '',
});
const mustBeDecimal = (value: string) => /^\d+(\.\d+)(\.\d+)?$/.test(value);
const rules = {
  schemaName: { required },
  schemaVersion: {
    required,
    mustBeDecimal: helpers.withMessage(
      'Must be a 2 or 3-part decimal value like x.y or x.y.z',
      mustBeDecimal
    ),
  },
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
    const justAttributeNames = attributes.value
      .filter((x) => x.name !== '')
      .map((attribute) => attribute.name);

    if (!justAttributeNames.length) {
      toast.error('Please provide at least one attribute for the schema');
      return;
    }

    const payload = {
      attributes: justAttributeNames,
      schema_name: formFields.schemaName,
      schema_version: formFields.schemaVersion,
    };

    // call store
    await governanceStore.createSchema(payload);
    toast.success(
      'Schema created. If it does not appear yet, refresh the table.'
    );
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
