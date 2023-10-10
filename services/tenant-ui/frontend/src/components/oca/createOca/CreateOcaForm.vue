<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <div>
        <!-- Credential -->
        <div class="field">
          <label
            for="selectedCred"
            :class="{ 'p-error': v$.selectedCred.$invalid && submitted }"
          >
            {{ $t('common.credentialId') }}
            <ProgressSpinner v-if="loading" />
          </label>

          <AutoComplete
            id="selectedCred"
            v-model="v$.selectedCred.$model"
            class="w-full"
            :disabled="loading"
            :suggestions="filteredCreds"
            :dropdown="true"
            option-label="label"
            force-selection
            @complete="searchCreds($event)"
          />
          <small v-if="v$.selectedCred.$invalid && submitted" class="p-error">{{
            v$.selectedCred.required.$message
          }}</small>
        </div>

        <!-- URL or bundle json -->
        <div>{{ $t('configuration.oca.bundleAssociationType') }}</div>
        <div class="mt-2">
          <RadioButton
            v-model="bundleType"
            input-id="radioUrl"
            name="radioUrl"
            value="url"
            @change="resetBundle"
          />
          <label for="radioUrl" class="ml-2">{{
            $t('configuration.oca.url')
          }}</label>
        </div>
        <div class="mt-2">
          <RadioButton
            v-model="bundleType"
            input-id="radioJson"
            name="radioJson"
            value="json"
            @change="resetBundle"
          />
          <label for="radioJson" class="ml-2">{{
            $t('configuration.oca.storedBundleJson')
          }}</label>
        </div>

        <!-- Bundle URL -->
        <div v-if="bundleType === 'url'" class="field mt-5">
          <label
            for="bundleUrl"
            :class="{ 'p-error': v$.bundleUrl.$invalid && submitted }"
            >{{ $t('configuration.oca.bundleUrl') }}</label
          >
          <InputText
            id="bundleUrl"
            v-model="v$.bundleUrl.$model"
            class="w-full"
            :class="{ 'p-invalid': v$.bundleUrl.$invalid && submitted }"
          />
          <span v-if="v$.bundleUrl.$error && submitted">
            <span v-for="(error, index) of v$.bundleUrl.$errors" :key="index">
              <small class="p-error">{{ error.$message }}</small>
            </span>
          </span>
          <small
            v-else-if="v$.bundleUrl.$invalid && submitted"
            class="p-error"
            >{{ v$.bundleUrl.required.$message }}</small
          >
        </div>

        <!-- Bundle JSON -->
        <div v-else class="mt-3">
          <span>{{ $t('configuration.oca.bundleJson') }}</span>
          <JsonEditorVue
            ref="jsonEditorVueRef"
            v-model="bundleJson"
            v-bind="jsonEditorSettings"
          />
        </div>

        <Button
          type="submit"
          :loading="loading"
          label="Add OCA"
          class="mt-5 w-full"
        />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
// Types
import { SchemaStorageRecord } from '@/types';
import {
  AddOcaRecordRequest,
  CredDefStorageRecord,
} from '@/types/acapyApi/acapyInterface';

// Vue
import { reactive, ref } from 'vue';
// PrimeVue / Validation
import { useVuelidate } from '@vuelidate/core';
import { required, requiredIf, url } from '@vuelidate/validators';
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import RadioButton from 'primevue/radiobutton';
import { useToast } from 'vue-toastification';
// State
import { useGovernanceStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other imports
import JsonEditorVue from 'json-editor-vue';

const toast = useToast();

// json editor config
const jsonEditorSettings = {
  mainMenuBar: false,
  mode: 'text' as any,
  statusBar: false,
  navigationBar: false,
  indentation: 2,
  tabSize: 2,
};

// Store values
const governanceStore = useGovernanceStore();
const { credentialDropdown, loading, storedCredDefs, storedSchemas } =
  storeToRefs(useGovernanceStore());

const emit = defineEmits(['closed', 'success']);

// Form / Validation setup
const bundleJson = ref({});
const bundleType = ref('url');
const filteredCreds = ref();
const formFields = reactive({
  selectedCred: undefined as any,
  bundleUrl: '',
});
const rules = {
  selectedCred: { required },
  bundleUrl: { url, required: requiredIf(() => bundleType.value === 'url') },
};
const v$ = useVuelidate(rules, formFields);

// Autocomplete setup
const searchCreds = (event: any) => {
  if (!event.query.trim().length) {
    filteredCreds.value = [...(credentialDropdown.value as any)];
  } else {
    filteredCreds.value = (credentialDropdown.value as any).filter(
      (cred: any) => {
        return cred.label.toLowerCase().includes(event.query.toLowerCase());
      }
    );
  }
};

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }

  try {
    // Get the specific schema to edit values for
    const schemaId = storedCredDefs.value.find(
      (cd: CredDefStorageRecord) =>
        cd.cred_def_id === formFields.selectedCred.value
    )?.schema_id;

    const schema = storedSchemas.value.find(
      (s: SchemaStorageRecord) => s.schema_id === schemaId
    );

    if (!schema)
      throw new Error('Unable to find schema for selected credential');

    const payload: AddOcaRecordRequest = {
      cred_def_id: formFields.selectedCred.value,
      schema_id: schema.schema_id,
    };
    if (bundleType.value === 'url') {
      payload.url = formFields.bundleUrl;
    } else if (bundleType.value === 'json') {
      payload.bundle = JSON.parse(bundleJson.value as string);
    }

    // call store
    await governanceStore.createOca(payload);
    toast.success('OCA Bundle associated with Credential Definition');
    emit('success');
    // close up on success
    emit('closed');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};

const resetBundle = () => {
  bundleJson.value = {};
  formFields.bundleUrl = '';
};
</script>
