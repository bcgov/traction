<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <div class="container">
        <div style="text-align: center">
          <div class="info-box">
            {{ $t('configuration.schemas.copyMessage') }}
          </div>
          <p style="font-weight: bold">{{ selectedSchema?.schema_id }}</p>
        </div>
        <div class="fields-contianer">
          <div class="field mt-2">
            <label
              for="name"
              :class="{
                'p-error':
                  v$.name.$invalid && submitted && !changedField('name'),
              }"
              >{{ $t('configuration.schemas.newName') }}</label
            >
            <InputText
              id="name"
              v-model="v$.name.$model"
              class="w-full"
              :class="{
                'p-invalid':
                  v$.name.$invalid && submitted && !changedField('name'),
              }"
            />
            <span v-if="v$.name.$error && submitted && !changedField('name')">
              <span v-for="(error, index) of v$.name.$errors" :key="index">
                <small class="p-error">{{ error.$message }}</small>
              </span>
            </span>
            <span v-else style="visibility: hidden">
              <small class="p-error">{{ $t('placeholder') }}</small>
            </span>
          </div>
          <div class="field mt-2">
            <label
              for="version"
              :class="{
                'p-error':
                  v$.version.$invalid && submitted && !changedField('version'),
              }"
              >{{ $t('configuration.schemas.newVersion') }}</label
            >
            <InputText
              id="version"
              v-model="v$.version.$model"
              class="w-full"
              :class="{
                'p-invalid':
                  v$.version.$invalid && submitted && !changedField('version'),
              }"
            />
            <span
              v-if="v$.version.$error && submitted && !changedField('version')"
            >
              <span v-for="(error, index) of v$.version.$errors" :key="index">
                <small class="p-error">{{ error.$message }}</small>
              </span>
            </span>
            <span v-else style="visibility: hidden">
              <small class="p-error">{{ $t('placeholder') }}</small>
            </span>
            <Button
              type="submit"
              :label="t('configuration.schemas.copy')"
              class="mt-5 w-full"
              :disabled="formFields.name === '' && formFields.version === ''"
            />
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { useVuelidate } from '@vuelidate/core';
import { helpers } from '@vuelidate/validators';
import { storeToRefs } from 'pinia';
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

const { selectedSchema } = storeToRefs(useGovernanceStore());
const governanceStore = useGovernanceStore();

const emit = defineEmits(['closed', 'success']);

// Form / Validation setup
const formFields = reactive({
  name: '',
  version: '',
});
const rules: { [key: string]: any } = {};

const changedField = (field: string) => {
  if (field === 'name' || field === 'version')
    if (formFields[field] !== selectedSchema.value?.schema?.[field])
      return true;
  return false;
};

const validCopy = () => {
  if (
    (changedField('name') && formFields.name !== '') ||
    (changedField('version') && formFields.version !== '')
  )
    return true;
  return false;
};

const setRule = (value: string | undefined, field: string) => {
  if (value)
    rules[field] = {
      validCopy: helpers.withMessage(
        t('configuration.schemas.invalidCopy', {
          field,
          value,
        }),
        validCopy
      ),
    };
};
if (selectedSchema.value) {
  setRule(selectedSchema.value.schema?.name, 'name');
  setRule(selectedSchema.value.schema?.version, 'version');
}

const v$ = useVuelidate(rules, formFields);

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  try {
    if (!selectedSchema.value) {
      throw new Error('No schema selected.');
    }
    const payload: SchemaSendRequest = {
      schema_name: formFields.name || selectedSchema.value.schema?.name || '',
      schema_version:
        formFields.version || selectedSchema.value.schema?.version || '',
      attributes: selectedSchema.value.schema?.attrNames || [],
    };

    await governanceStore.createSchema(payload);

    toast.success(t('configuration.schemas.copySent'));
    emit('success');
    // close up on success
    emit('closed', payload);
  } catch (error) {
    errorHandler(error, t('configuration.schemas.alreadyExists'));
  } finally {
    submitted.value = false;
  }
};
</script>

<style scoped>
.container {
  min-width: 300px;
  display: inline-block;
  margin: 0 auto;
  text-align: left;
}
.fields-container {
  width: 50%;
  margin: 0% 25%;
}
form {
  display: block;
  text-align: center;
}
.info-box {
  background-color: #eff6ff;
  border-radius: 5px;
  padding: 10px;
  margin-bottom: 10px;
}
</style>
