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
            >Credential Name
            <ProgressSpinner v-if="credsLoading" />
          </label>

          <AutoComplete
            id="selectedCred"
            v-model="v$.selectedCred.$model"
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

        <!-- Contact -->
        <div class="field mt-5">
          <label
            for="selectedContact"
            :class="{ 'p-error': v$.selectedContact.$invalid && submitted }"
            >Connection Name
            <ProgressSpinner v-if="contactLoading" />
          </label>

          <AutoComplete
            id="selectedContact"
            v-model="v$.selectedContact.$model"
            :disabled="contactLoading"
            :suggestions="filteredContacts"
            :dropdown="true"
            option-label="label"
            force-selection
            @complete="searchContacts($event)"
          />
          <small
            v-if="v$.selectedContact.$invalid && submitted"
            class="p-error"
            >{{ v$.selectedContact.required.$message }}</small
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
              >Credential Value</label
            >
            <Button
              label="Enter Credential Value"
              class="p-button-link flex justify-content-end"
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
            rows="20"
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
          :disabled="contactLoading || credsLoading"
          :loading="contactLoading || credsLoading"
        />
      </div>

      <!-- Credential values -->
      <div v-else>
        <Button
          icon="pi pi-arrow-left"
          class="p-button-rounded p-button-text mr-2 pt-3"
          @click="showEditCredValues = false"
        />
        <strong>{{ formFields.selectedCred.label }}</strong>

        <div class="field mt-5">
          <label for="credentialValuesEdit"
            >Credential Field Values
            <small
              >(Schema: {{ schemaForSelectedCred.schema_name }}
              {{ schemaForSelectedCred.version }})</small
            >
          </label>
          <!-- TODO: This is replaced with the dynamic field creation  -->
          <Textarea
            id="credentialValuesEdit"
            v-model="v$.credentialValuesEditing.$model"
            :auto-resize="true"
            rows="20"
            cols="50"
            class="w-full"
          />

          <Button label="Save" class="mt-5 w-full" @click="saveCredValues" />
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
// Vue
import { computed, reactive, ref } from 'vue';
// PrimeVue / Validation
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';
import ProgressSpinner from 'primevue/progressspinner';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { storeToRefs } from 'pinia';
import {
  useContactsStore,
  useGovernanceStore,
  useIssuerStore,
} from '../../../store';
// Other imports
import { useToast } from 'vue-toastification';

const toast = useToast();

// Store values
const { loading: contactLoading, contactsDropdown } = storeToRefs(
  useContactsStore()
);
const {
  loading: credsLoading,
  credentialTemplateDropdown,
  credentialTemplates,
  schemaTemplates,
} = storeToRefs(useGovernanceStore());
const issuerStore = useIssuerStore();

// Form and Validation
// TODO: this one replaced with dynamic field display
const credentialValuesRaw = ref([]);
const filteredCreds = ref();
const filteredContacts = ref();
const schemaForSelectedCred = ref();
const showEditCredValues = ref(false);
const formFields = reactive({
  credentialValuesEditing: '',
  credentialValuesPretty: '',
  // This is not good typescript but need an object with fields
  // in a dropdown that displays a string that can be blank. TODO
  selectedContact: undefined as any,
  selectedCred: undefined as any,
});
const rules = {
  credentialValuesEditing: {},
  credentialValuesPretty: { required },
  selectedCred: { required },
  selectedContact: { required },
};
const v$ = useVuelidate(rules, formFields);

// Autocomplete setup
// These can maybe be generalized into a util function (for all dropdown searches)
const searchContacts = (event: any) => {
  if (!event.query.trim().length) {
    filteredContacts.value = [...contactsDropdown.value];
  } else {
    filteredContacts.value = contactsDropdown.value.filter((contact) => {
      return contact.label.toLowerCase().includes(event.query.toLowerCase());
    });
  }
};
const searchCreds = (event: any) => {
  if (!event.query.trim().length) {
    filteredCreds.value = [...credentialTemplateDropdown.value];
  } else {
    filteredCreds.value = credentialTemplateDropdown.value.filter((cred) => {
      return cred.label.toLowerCase().includes(event.query.toLowerCase());
    });
  }
};

// Editing the credential
const editCredentialValues = () => {
  showEditCredValues.value = true;

  // Popuplate cred editor if it's not already been edited
  if (!formFields.credentialValuesPretty.length) {
    // Get the specific schema to edit values for
    const schemaId = credentialTemplates.value.find(
      (ct: any) => ct.credential_template_id === formFields.selectedCred.value
    ).schema_template_id;
    const schema = schemaTemplates.value.find(
      (st: any) => st.schema_template_id === schemaId
    );
    schemaForSelectedCred.value = schema;

    const schemaFillIn = schemaForSelectedCred.value.attributes.map(
      (a: string) => {
        return {
          name: `${a}`,
          value: '',
        };
      }
    );
    console.log(schemaFillIn);
    formFields.credentialValuesEditing = JSON.stringify(
      schemaFillIn,
      undefined,
      2
    );
  }
};
const saveCredValues = () => {
  // TODO: to be replaced with dynamic form field component
  credentialValuesRaw.value = JSON.parse(formFields.credentialValuesEditing);
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
      contact_id: formFields.selectedContact.value,
      credential_template_id: formFields.selectedCred.value,
      attributes: credentialValuesRaw.value,
      tags: [],
    };

    // call store
    await issuerStore.offerCredential(payload);
    toast.info('Credential Offer Sent');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>
