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
            >{{ $t('issue.schemaName') }}</label
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
            >{{ $t('issue.schemaVersion') }}</label
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
        <h4 style="margin-bottom: 0.5rem; font-weight: normal">
          {{ $t('issue.attributes') }}
        </h4>
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
            @keydown.enter.prevent="addAttribute()"
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
        <Button
          type="submit"
          :label="t('configuration.schemas.create')"
          class="mt-5 w-full"
        />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { useVuelidate } from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';

import errorHandler from '@/helpers/errorHandler';
import { useGovernanceStore } from '@/store';
import { SchemaSendRequest } from '@/types/acapyApi/acapyInterface';

const toast = useToast();
const { t } = useI18n();

// Store values
const governanceStore = useGovernanceStore();

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
      toast.error(t('configuration.schemas.emptyAttributes'));
      return;
    }

    const payload: SchemaSendRequest = {
      attributes: justAttributeNames,
      schema_name: formFields.schemaName,
      schema_version: formFields.schemaVersion,
    };

    await governanceStore.createSchema(payload);

    toast.success(t('configuration.schemas.postStart'));
    emit('success');
    emit('closed', payload);
  } catch (error) {
    errorHandler(error, t('configuration.schemas.alredyExists'));
  } finally {
    submitted.value = false;
  }
};
</script>
