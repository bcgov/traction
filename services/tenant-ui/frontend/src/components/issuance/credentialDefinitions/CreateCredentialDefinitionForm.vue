<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Schema -->
    <div class="field">
      <label for="schema">{{ $t('issue.schema') }}</label>
      <div v-if="schema">
        <InputText
          id="schema"
          :value="schema.schema.name"
          readonly
          :disabled="loading"
          class="w-full"
        />
        <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
        <small>id: {{ schema.schema_id }}</small>
      </div>
      <div v-else-if="schemas?.length">
        <Dropdown
          id="schema_id"
          v-model="formFields.schema_id"
          :options="storedSchemas"
          option-value="schema_id"
          option-label="schema_id"
          :disabled="loading"
          class="w-full"
          :placeholder="t('configuration.credentialDefinitions.selectSchema')"
        />
      </div>
    </div>
    <!-- Tag -->
    <ValidatedField
      :validation="v$"
      :submitted="submitted"
      :loading="loading"
      :field-name="'creddef_tag'"
      :label="$t('issue.credentialDefinitionTag')"
    />
    <!-- Revocation -->
    <div class="field">
      <div class="field-checkbox">
        <Checkbox
          v-model="formFields.creddef_revocation_enabled"
          :disabled="loading"
          input-id="creddef_revocation_enabled"
          :binary="true"
          @change="resetRegSize"
        />
        <label for="creddef_revocation_enabled">{{
          $t('issue.revocationEnabled')
        }}</label>
      </div>
    </div>
    <div v-if="formFields.creddef_revocation_enabled">
      <ValidatedField
        :validation="v$"
        :submitted="submitted"
        :loading="loading"
        :field-name="'creddef_revocation_registry_size'"
        :label="$t('issue.revocationRegistrySize')"
      />
    </div>
    <Button
      type="submit"
      label="Create"
      class="mt-4 w-full"
      :disabled="loading || (formFields.schema_id === '' && !schema)"
      :loading="loading"
    />
  </form>
</template>
<script setup lang="ts">
import { useVuelidate } from '@vuelidate/core';
import {
  between,
  helpers,
  integer,
  minLength,
  required,
  requiredIf,
} from '@vuelidate/validators';
import { storeToRefs } from 'pinia';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import { PropType, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';

import ValidatedField from '@/components/common/ValidatedField.vue';
import errorHandler from '@/helpers/errorHandler';
import { useGovernanceStore } from '@/store';
import { CredentialDefinitionSendRequest } from '@/types/acapyApi/acapyInterface';

const props = defineProps({
  schema: {
    type: Object,
    required: false,
    default: undefined,
  },
  schemas: {
    type: Array as PropType<any[]>,
    required: false,
    default: undefined,
  },
});

const toast = useToast();
const { t } = useI18n();

const governanceStore = useGovernanceStore();

// use the loading state from the store to disable the button...
const { loading, storedSchemas } = storeToRefs(useGovernanceStore());

const emit = defineEmits(['closed', 'success']);

// Validation
const formFields = reactive({
  schema_id: '',
  creddef_tag: '',
  creddef_revocation_enabled: false,
  creddef_revocation_registry_size: '4',
});

const tagNotUsed = (value: string) => {
  let activeSchema;
  if (props.schema) activeSchema = props.schema;
  else if (props.schemas) {
    activeSchema = props.schemas.find(
      (schema: any) => schema.schema_id === formFields.schema_id
    );
  }

  if (!activeSchema) return true;

  return !activeSchema.credentialDefinitions.some(
    (credDef: any) => credDef.tag === value
  );
};

const rules = {
  creddef_tag: {
    required,
    minLength: minLength(1),
    tagNotUsed: helpers.withMessage(
      t(
        'configuration.credentialDefinitions.tagAlreadyUsed',
        formFields.creddef_tag
      ),
      tagNotUsed
    ),
  },
  creddef_revocation_registry_size: {
    integer,
    betweenValue: between(4, 32768),
    requiredEnabled: requiredIf(formFields.creddef_revocation_registry_size),
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

  const payload: CredentialDefinitionSendRequest = {
    tag: formFields.creddef_tag,
    support_revocation: formFields.creddef_revocation_enabled,
    schema_id: props.schema ? props.schema.schema_id : formFields.schema_id,
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
    await governanceStore.createCredentialDefinition(payload);

    toast.success(t('configuration.credentialDefinitions.postStart'));
    emit('success');
    emit('closed', payload);
  } catch (error: any) {
    errorHandler({
      error,
      existsMessage: t('configuration.credentialDefinitions.alreadyExists'),
    });
  } finally {
    submitted.value = false;
  }
};

// Set reg size back to default if you disable revocation, for validation cleanliness
const resetRegSize = () => {
  formFields.creddef_revocation_registry_size = '4';
};
</script>
