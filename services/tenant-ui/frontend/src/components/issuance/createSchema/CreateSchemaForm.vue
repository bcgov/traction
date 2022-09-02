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
        <hr />
        <!-- attributes -->
        <div class="flex justify-content-between">
          <label>Attributes</label>
          <button
            class="p-button p-component p-button-icon-only p-button-rounded p-button-outlined"
            type="button"
            @click="addAttribute"
          >
            <span class="pi pi-plus p-button-icon"></span>
          </button>
        </div>
        <div v-for="(item, index) in attributes" :key="index" class="row">
          <InputText v-model="item.name" type="text" name="{{ index }}" />
          <button
            class="p-button p-component p-button-icon-only p-button-rounded p-button-danger p-button-text p-float-left"
            type="button"
            @click="removeAttribute(index)"
          >
            <span class="pi pi-times p-button-icon"></span>
          </button>
        </div>
        <Button type="submit" label="Create Schema" class="mt-5 w-full" />
      </div>
    </form>
  </div>
</template>
<script setup lang="ts">
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';

import { reactive, ref } from 'vue';
import { useToast } from 'vue-toastification';
import { useGovernanceStore } from '@/store';
import { storeToRefs } from 'pinia';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';

const toast = useToast();

const governanceStore = useGovernanceStore();

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
const rules = {
  schemaName: { required },
  schemaVersion: { required },
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
    const justAttributeNames = attributes.value.map(
      (attribute) => attribute.name
    );
    const payload = {
      schema_definition: {
        schema_name: formFields.schemaName,
        schema_version: formFields.schemaVersion,
        attributes: justAttributeNames,
      },
      name: formFields.schemaName,
      tags: [],
    };

    // call store
    await governanceStore.createSchemaTemplate(payload);
    toast.info('Schema created');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>

<style scoped>
.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin: 20px 0;
}
/* TODO: app-wide style (like form layout) to go in a global scss */
.field > label,
.field > small.p-error {
  display: block !important;
}
</style>
