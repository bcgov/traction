<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <div class="container">
        <div v-if="isCopy" style="text-align: center">
          <div class="info-box">
            {{ $t('configuration.schemas.copyMessage') }}
          </div>
          <p style="font-weight: bold">{{ selectedSchema?.schema_id }}</p>
        </div>
        <!-- schema name -->
        <div class="field mt-5">
          <label for="name" :class="{ 'p-error': isError(v$, 'name') }">{{
            $t('issue.schemaName')
          }}</label>
          <InputText
            id="name"
            v-model="v$.name.$model"
            class="w-full"
            :class="{ 'p-invalid': isError(v$, 'name') }"
          />
          <span v-if="isError(v$, 'name')">
            <span v-for="(error, index) of v$.name.$errors" :key="index">
              <small class="p-error">{{ error.$message }}</small>
            </span>
          </span>
          <span v-else style="visibility: hidden">
            <small class="p-error">{{ $t('placeholder') }}</small>
          </span>
        </div>
        <!-- schema version -->
        <div class="field mt-3">
          <label for="version" :class="{ 'p-error': isError(v$, 'version') }">{{
            $t('issue.schemaVersion')
          }}</label>
          <InputText
            id="version"
            v-model="v$.version.$model"
            class="w-full"
            :class="{ 'p-invalid': isError(v$, 'version') }"
          />
          <span v-if="isError(v$, 'version')">
            <span v-for="(error, index) of v$.version.$errors" :key="index">
              <small class="p-error">{{ error.$message }}</small>
            </span>
          </span>
        </div>
        <!-- attributes -->
        <Attributes ref="attributes" :initial-attributes="initialAttributes" />
        <Button
          type="submit"
          :label="t('configuration.schemas.create')"
          class="mt-5 w-full"
          :disabled="formFields.name === '' && formFields.version === ''"
        />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
// Libraries
import { useVuelidate } from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';
import { storeToRefs } from 'pinia';
// Source
import errorHandler from '@/helpers/errorHandler';
import { useGovernanceStore } from '@/store';
import { SchemaSendRequest } from '@/types/acapyApi/acapyInterface';
import { Attribute } from '@/types';
import Attributes from './Attributes.vue';

const toast = useToast();
const { t } = useI18n();

const governanceStore = useGovernanceStore();
const { selectedSchema } = storeToRefs(useGovernanceStore());

const emit = defineEmits(['closed', 'success']);
const attributes = ref();

const props = defineProps({
  isCopy: {
    type: Boolean,
    required: false,
    default: false,
  },
  initialAttributes: {
    type: Array<Attribute>,
    required: false,
    default: [],
  },
  onClose: {
    type: Function,
    required: false,
    default: () => {},
  },
});

// Form / Validation setup
const formFields = reactive({
  name: '',
  version: '',
});

let rules: { [key: string]: any } = {};

const mustBeDecimal = (value: string) => /^\d+(\.\d+)(\.\d+)?$/.test(value);
rules = {
  name: { required },
  version: {
    required,
    mustBeDecimal: helpers.withMessage(
      t('configuration.schemas.mustBeDecimal'),
      mustBeDecimal
    ),
  },
};

const changedField = (field: string) => {
  if (field === 'name' || field === 'version')
    if (formFields[field] !== selectedSchema.value?.schema?.[field])
      return true;
  return false;
};

const isError = (v: any, field: string) => {
  if (props.isCopy)
    return v[field].$error && submitted.value && !changedField(field);
  return v[field].$error && submitted.value;
};

// Add copy rules if isCopy
if (props.isCopy) {
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
        ...rules[field],
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

  delete rules.name.required;
  delete rules.version.required;
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
    const attributeNames = attributes.value?.attributes
      .filter((x: Attribute) => x.name !== '')
      .map((attribute: Attribute) => attribute.name);

    if (!attributeNames.length) {
      toast.error(t('configuration.schemas.emptyAttributes'));
      return;
    }

    const payload: SchemaSendRequest = {
      attributes: attributeNames,
      schema_name: formFields.name || selectedSchema.value?.schema?.name || '',
      schema_version:
        formFields.version || selectedSchema.value?.schema?.version || '',
    };

    await governanceStore.createSchema(payload);

    toast.success(t('configuration.schemas.postStart'));
    emit('success');
    emit('closed', payload);
    if (props.onClose) props.onClose(payload);
  } catch (error) {
    errorHandler(error, t('configuration.schemas.alreadyExists'));
  } finally {
    submitted.value = false;
  }
};
</script>

<style scoped>
.container {
  min-width: 400px;
  display: inline-block;
  margin: 0 auto;
  text-align: left;
}
.fields-container {
  width: 80%;
  margin: 0% 10%;
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
