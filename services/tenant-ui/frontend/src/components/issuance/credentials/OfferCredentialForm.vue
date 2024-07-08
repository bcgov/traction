<template>
  <div>
    <form @submit.prevent="handleSubmit(!v$.$invalid)">
      <!-- Main Form -->
      <div v-if="!showEditCredValues">
        <!-- Credential -->
        <div class="field">
          <label
            for="selectedCred"
            :class="{ 'p-error': v$.selectedCred.$invalid && submitted }"
            >{{ $t('common.credentialId') }}
            <ProgressSpinner v-if="credsLoading" />
          </label>

          <AutoComplete
            id="selectedCred"
            v-model="v$.selectedCred.$model"
            class="w-full"
            :disabled="credsLoading"
            :suggestions="filteredCreds"
            :dropdown="true"
            option-label="label"
            force-selection
            @complete="searchCreds($event)"
            @change="resetCredValues"
          />
          <small v-if="v$.selectedCred.$invalid && submitted" class="p-error">{{
            v$.selectedCred.required.$message
          }}</small>
        </div>

        <!-- Connection -->
        <div class="field mt-5">
          <label
            for="selectedConnection"
            :class="{ 'p-error': v$.selectedConnection.$invalid && submitted }"
            >{{ $t('common.connectionName') }}
            <ProgressSpinner v-if="connectionLoading" />
          </label>

          <AutoComplete
            id="selectedConnection"
            v-model="v$.selectedConnection.$model"
            class="w-full"
            :disabled="connectionLoading"
            :suggestions="filteredConnections"
            :dropdown="true"
            option-label="label"
            force-selection
            @complete="searchConnections($event)"
          />
          <small
            v-if="v$.selectedConnection.$invalid && submitted"
            class="p-error"
            >{{ v$.selectedConnection.required.$message }}</small
          >
        </div>

        <!-- Cred Values -->
        <div class="field mt-5">
          <div class="flex justify-content-between">
            <label
              for="credentialValues"
              class="flex justify-content-start"
              :class="{
                'p-error': v$.credentialValuesPretty.$invalid && submitted,
              }"
            >
              {{ $t('issue.credentialFieldValues') }}
            </label>
            <Button
              label="Enter Credential Value"
              class="p-button-link flex justify-content-end pt-1"
              :disabled="!v$.selectedCred.$model"
              @click="editCredentialValues"
            />
          </div>
          <Textarea
            id="credentialValuesPretty"
            v-model="v$.credentialValuesPretty.$model"
            :class="{
              'w-full': true,
              'p-invalid': v$.credentialValuesPretty.$invalid && submitted,
            }"
            :auto-resize="true"
            rows="15"
            cols="50"
            readonly
          />
          <small
            v-if="v$.credentialValuesPretty.$invalid && submitted"
            class="p-error"
            >{{ v$.credentialValuesPretty.required.$message }}</small
          >
        </div>

        <Button
          type="submit"
          label="Send Offer"
          class="mt-5 w-full"
          :disabled="connectionLoading || credsLoading || issueLoading"
          :loading="connectionLoading || credsLoading || issueLoading"
        />
      </div>

      <!-- Credential values -->
      <div v-else>
        <EnterCredentialValues
          :existing-credential-values="credentialValuesRaw"
          :header="formFields.selectedCred.label"
          :schema-for-selected-cred="schemaForSelectedCred"
          @back="showEditCredValues = false"
          @save="saveCredValues"
        />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// PrimeVue / Validation / etc
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';
import ProgressSpinner from 'primevue/progressspinner';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
// State
import { storeToRefs } from 'pinia';
import {
  useConnectionStore,
  useGovernanceStore,
  useIssuerStore,
} from '@/store';
// Other components
import EnterCredentialValues from './EnterCredentialValues.vue';

const toast = useToast();

// Store values
const { loading: connectionLoading, connectionsDropdown } =
  storeToRefs(useConnectionStore());
const {
  loading: credsLoading,
  credentialDropdown,
  storedCredDefs,
  storedSchemas,
} = storeToRefs(useGovernanceStore());
const { loading: issueLoading } = storeToRefs(useIssuerStore());
const issuerStore = useIssuerStore();

const emit = defineEmits(['closed', 'success']);

// Form and Validation
const credentialValuesRaw = ref([] as { name: string; value: string }[]);
const filteredCreds = ref();
const filteredConnections = ref();
const schemaForSelectedCred = ref();
const showEditCredValues = ref(false);
const formFields = reactive({
  credentialValuesEditing: '',
  credentialValuesPretty: '',
  // This is not good typescript but need an object with fields
  // in a dropdown that displays a string that can be blank. TODO
  selectedConnection: undefined as any,
  selectedCred: undefined as any,
});
const rules = {
  credentialValuesEditing: {},
  credentialValuesPretty: { required },
  selectedCred: { required },
  selectedConnection: { required },
};
const v$ = useVuelidate(rules, formFields);

// Autocomplete setup
// These can maybe be generalized into a util function (for all dropdown searches)
const searchConnections = (event: any) => {
  if (!event.query.trim().length) {
    filteredConnections.value = [...(connectionsDropdown as any).value];
  } else {
    filteredConnections.value = (connectionsDropdown.value as any).filter(
      (connection: any) => {
        return connection.label
          .toLowerCase()
          .includes(event.query.toLowerCase());
      }
    );
  }
};
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

// Editing the credential
const editCredentialValues = () => {
  // Get the specific schema to edit values for
  const schemaId = storedCredDefs.value.find(
    (cd: any) => cd.cred_def_id === formFields.selectedCred.value
  )?.schema_id;
  const schema = storedSchemas.value.find((s: any) => s.schema_id === schemaId);
  schemaForSelectedCred.value = schema;

  // Open the editor
  showEditCredValues.value = true;
};
const saveCredValues = (credEmitted: { name: string; value: string }[]) => {
  console.log(credEmitted);
  credentialValuesRaw.value = credEmitted;
  formFields.credentialValuesPretty = '';
  credentialValuesRaw.value.forEach((c: any) => {
    formFields.credentialValuesPretty += `${c.name}: ${c.value} \n`;
  });
  showEditCredValues.value = false;
};
const resetCredValues = () => {
  credentialValuesRaw.value = [];
  formFields.credentialValuesPretty = '';
  formFields.credentialValuesEditing = '';
};

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  try {
    const payload = {
      auto_issue: true,
      auto_remove: false,
      connection_id: formFields.selectedConnection.value,
      credential_preview: {
        '@type': 'issue-credential/2.0/credential-preview',
        attributes: credentialValuesRaw.value,
      },
      filter: {
        indy: {
          cred_def_id: formFields.selectedCred.value,
        },
      },
      trace: false,
    };

    // call store
    await issuerStore.offerCredential(payload);
    toast.info('Credential Offer Sent');
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
