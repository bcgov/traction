<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <div class="container">
        <div style="text-align: center">
          <div class="info-box">
            {{ $t('configuration.credentialDefinitions.copyInfo1') }}
            <h4 style="font-weight: bold">
              {{ selectedCredentialDefinition?.cred_def_id }}
            </h4>
            {{ $t('configuration.credentialDefinitions.copyInfo2') }}
            <h4 style="font-weight: bold">
              {{ selectedCredentialDefinition?.schema_id }}
            </h4>
            {{ $t('configuration.credentialDefinitions.copyInfo3') }}
          </div>
        </div>
        <div class="fields-container">
          <div class="mt-5">
            <ValidatedField
              :validation="v$"
              :submitted="submitted"
              :loading="loading"
              :field-name="'tag'"
              :label="$t('configuration.credentialDefinitions.newTag')"
            />
            <Button
              type="submit"
              :label="t('configuration.credentialDefinitions.copy')"
              class="mt-2 w-full"
              :loading="loading"
            />
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { useVuelidate } from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import { storeToRefs } from 'pinia';
import Button from 'primevue/button';
import { reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';

import ValidatedField from '@/components/common/ValidatedField.vue';
import errorHandler from '@/helpers/errorHandler';
import { useGovernanceStore } from '@/store';

const toast = useToast();
const { t } = useI18n();

const { loading, selectedCredentialDefinition, storedCredDefs } =
  storeToRefs(useGovernanceStore());
const governanceStore = useGovernanceStore();

const emit = defineEmits(['closed', 'success']);

// Form / Validation setup
const formFields = reactive({
  tag: '',
});

const validCopy = () => {
  for (const credDef of storedCredDefs.value) {
    if (
      credDef.tag === formFields.tag &&
      credDef.schema_id === selectedCredentialDefinition.value?.schema_id
    ) {
      return false;
    }
  }
  return true;
};

const rules: { [key: string]: any } = {
  tag: {
    required: helpers.withMessage(
      t('configuration.credentialDefinitions.tagRequired'),
      required
    ),
    validCopy: helpers.withMessage(
      t('configuration.credentialDefinitions.tagAlreadyUsed'),
      validCopy
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
    if (!selectedCredentialDefinition.value) {
      throw new Error('No schema selected.');
    }
    const payload = selectedCredentialDefinition.value;
    payload.tag = formFields.tag;

    await governanceStore.createCredentialDefinition(payload);

    toast.success(t('configuration.credentialDefinitions.postStart'));
    emit('success');
    emit('closed', payload);
  } catch (error) {
    errorHandler({
      error,
      existsMessage: t('configuration.credentialDefinitions.alreadyExists'),
    });
  } finally {
    submitted.value = false;
  }
};
</script>

<style scoped>
.container {
  min-width: 500px;
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
