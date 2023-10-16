<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <div class="container">
      <div style="text-align: center">
        <div class="info-box">
          <p>
            {{ t('configuration.schemas.addFromLedgerInfo') }}
          </p>
        </div>
      </div>
      <div class="fields-container mt-5">
        <ValidatedField
          :center-placeholder="true"
          :validation="v$"
          :submitted="submitted"
          :loading="loading"
          :field-name="'schemaId'"
          :placeholder="t('configuration.schemas.id')"
        />
        <Button
          type="submit"
          :label="t('configuration.schemas.add')"
          class="mt-2 w-full"
          :loading="loading"
        />
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
// Libraries
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import Button from 'primevue/button';
import { reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';
// Source
import ValidatedField from '@/components/common/ValidatedField.vue';
import errorHandler from '@/helpers/errorHandler';
import { useGovernanceStore } from '@/store';
import { AddSchemaFromLedgerRequest } from '@/types';
import { storeToRefs } from 'pinia';

const toast = useToast();
const { t } = useI18n();

const emit = defineEmits(['closed', 'success']);

const governanceStore = useGovernanceStore();
const { loading } = storeToRefs(useGovernanceStore());

// Form / Validation setup
const formFields = reactive({
  schemaId: '',
});
const rules = {
  schemaId: { required },
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
    const payload: AddSchemaFromLedgerRequest = {
      schema_id: formFields.schemaId,
    };

    // call store
    await governanceStore.addSchemaFromLedgerToStorage(payload);
    toast.success(
      t('configuration.schemas.addedFromLedger', {
        schemaId: formFields.schemaId,
      })
    );

    governanceStore.setSelectedSchemaById(formFields.schemaId);
    emit('success');
    // close up on success
    emit('closed');
  } catch (error) {
    errorHandler({
      error,
      badRequestMessage: t('configuration.schemas.addNotExists'),
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
  width: 90%;
  margin: 0% 5%;
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
