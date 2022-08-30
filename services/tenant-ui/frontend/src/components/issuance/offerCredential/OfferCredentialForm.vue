<template>
    <div>
        <form @submit.prevent="handleSubmit(!v$.$invalid)">
            <!-- Main Form -->
            <div v-if="!showEditCredValues">
                <!-- Credential -->
                <div class="field">
                    <label for="selectedCred" :class="{ 'p-error': v$.selectedCred.$invalid && submitted }">Credential
                        Name
                        <ProgressSpinner v-if="ctLoad" />
                    </label>

                    <AutoComplete id="selectedCred" v-model="v$.selectedCred.$model" :disabled="ctLoad"
                        :suggestions="filteredCreds" @complete="searchCreds($event)" :dropdown="true"
                        optionLabel="label" forceSelection />
                    <small v-if="v$.selectedCred.$invalid && submitted" class="p-error">{{
                            v$.selectedCred.required.$message
                    }}</small>
                </div>

                <!-- Contact -->
                <div class="field mt-5">
                    <label for="selectedContact"
                        :class="{ 'p-error': v$.selectedContact.$invalid && submitted }">Connection
                        Name
                        <ProgressSpinner v-if="cLoad" />
                    </label>

                    <AutoComplete id="selectedContact" v-model="v$.selectedContact.$model" :disabled="cLoad"
                        :suggestions="filteredContacts" @complete="searchContacts($event)" :dropdown="true"
                        optionLabel="label" forceSelection />
                    <small v-if="v$.selectedContact.$invalid && submitted" class="p-error">{{
                            v$.selectedContact.required.$message
                    }}</small>
                </div>

                <!-- Cred Values -->
                <div class="field mt-5">
                    <div class="flex justify-content-between">
                        <label for="credentialValues" class="flex justify-content-start"
                            :class="{ 'p-error': v$.credentialValues.$invalid && submitted }">Credential Value</label>
                        <Button label="Enter Credential Value" class="p-button-link flex justify-content-end"
                            :disabled="!v$.selectedCred.$model" @click="editCredentialValues" />
                    </div>
                    <Textarea id="credentialValues" v-model="v$.credentialValues.$model"
                        :class="{ 'w-full': true, 'p-invalid': v$.credentialValues.$invalid && submitted }"
                        :autoResize="true" rows="20" cols="50" readonly />
                    <small v-if="v$.credentialValues.$invalid && submitted" class="p-error">{{
                            v$.credentialValues.required.$message
                    }}</small>
                </div>

                <Button type="submit" label="Send Offer" class="mt-5 w-full" :disabled="loading" :loading="loading" />
            </div>

            <!-- Credential values -->
            <div v-else>
                <Button icon="pi pi-arrow-left" class="p-button-rounded p-button-text mr-2 pt-3"
                    @click="showEditCredValues = false" />
                <strong>{{ v$.selectedCred.$model.label }}</strong>

                <div class="field mt-5">
                    <label for="credentialValues"
                        :class="{ 'p-error': v$.credentialValues.$invalid && submitted }">Credential Field
                        Values
                        <small>(Schema: {{ schemaForSelectedCred.schema_name }} {{ schemaForSelectedCred.version
                        }})</small>
                    </label>
                    <!-- TODO: This is replaced with the dynamic field creation  -->
                    <Textarea id="credentialValuesEdit" v-model="v$.credentialValuesEditing.$model" :autoResize="true"
                        rows="20" cols="50" class="w-full" />

                    <Button label="Save" class="mt-5 w-full" @click="saveCredValues" />
                </div>

            </div>
        </form>
    </div>
</template>

<script setup lang="ts">
// Vue
import { computed, reactive, ref } from "vue";
// PrimeVue / Validation
import AutoComplete from 'primevue/autocomplete';
import Button from "primevue/button";
import Textarea from "primevue/textarea";
import ProgressSpinner from "primevue/progressspinner";
import { required } from "@vuelidate/validators";
import { useVuelidate } from "@vuelidate/core";
// State
import { storeToRefs } from "pinia";
import { useContactsStore, useGovernanceStore } from '../../../store';
// Other imports
import { useToast } from "vue-toastification";

const toast = useToast();

// Store values
const {
    loading: cLoad, contactsDropdown
} = storeToRefs(useContactsStore());
const {
    loading: ctLoad, credentialTemplateDropdown, credentialTemplates, schemaTemplates
} = storeToRefs(useGovernanceStore());
const loading = computed(() => cLoad.value || ctLoad.value)

// Form and Validation
// TODO: this one replaced with dynamic field display
const filteredCreds = ref();
const filteredContacts = ref();
const schemaForSelectedCred = ref({});
const showEditCredValues = ref(false);
const formFields = reactive({
    credentialValuesEditing: '',
    credentialValues: '',
    selectedContact: '',
    selectedCred: ''
});
const rules = {
    credentialValuesEditing: {},
    credentialValues: { required },
    selectedCred: { required },
    selectedContact: { required }
}
const v$ = useVuelidate(rules, formFields)

// Autocomplete setup
// These can maybe be generalized into a util function (for all dropdown searches)
const searchContacts = (event: any) => {
    if (!event.query.trim().length) {
        filteredContacts.value = [...contactsDropdown.value];
    }
    else {
        filteredContacts.value = contactsDropdown.value.filter((contact) => {
            return contact.label.toLowerCase().includes(event.query.toLowerCase());
        });
    };
};
const searchCreds = (event: any) => {
    if (!event.query.trim().length) {
        filteredCreds.value = [...credentialTemplateDropdown.value];
    }
    else {
        filteredCreds.value = credentialTemplateDropdown.value.filter((cred) => {
            return cred.label.toLowerCase().includes(event.query.toLowerCase());
        });
    };
};

// Editing the credential
const editCredentialValues = () => {
    showEditCredValues.value = true;

    // Popuplate cred editor if it's not already been edited
    console.log(formFields.credentialValues.length);
    if (!formFields.credentialValues.length) {
        // Get the specific schema to edit values for
        const schemaId = credentialTemplates.value.find(ct => ct.credential_template_id === formFields.selectedCred.value).schema_template_id;
        const schema = schemaTemplates.value.find(st => st.schema_template_id === schemaId);
        schemaForSelectedCred.value = schema;

        const schemaFillIn = schemaForSelectedCred.value.attributes.map(a => {
            return {
                name: `${a}`,
                value: ""
            }
        });
        console.log(schemaFillIn);
        formFields.credentialValuesEditing = JSON.stringify(schemaFillIn, 0, 2);
    }
}
const saveCredValues = () => {
    // TODO: to be replaced with dynamic form field component
    formFields.credentialValues = formFields.credentialValuesEditing;
    showEditCredValues.value = false;
}

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
    submitted.value = true;

    if (!isFormValid) {
        return;
    }
}
</script>

<style>
/* TODO: app-wide style (like form layout) to go in a global scss */
.field>label,
.field>small.p-error {
    display: block !important;
}

.field>label>.p-progress-spinner {
    height: 1em;
    width: 1em;
}
</style>