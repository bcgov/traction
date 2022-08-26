<template>
    <div>
        {{ credentialTemplateDropdown.length }} <br>
        Contacts: {{ contactsDropdown.length }}
        <form @submit.prevent="handleSubmit(!v$.$invalid)">

            {{ contactsDropdown }} <br><br> <br> <br>
            {{ v$.selectedContact.$model }} <br> <br> <br>
            <!-- Credential -->
            <div class="field">
                <span class="p-float-label">
                    <AutoComplete v-model="v$.selectedCred.$model" :suggestions="filteredCreds"
                        @complete="searchCreds($event)" :dropdown="true" optionLabel="label" forceSelection />
                    <label>Credential Name</label>
                </span>
            </div>
            <!-- Contact -->
            <div class="field mt-5">
                <span class="p-float-label">
                    <AutoComplete v-model="v$.selectedContact.$model" :suggestions="filteredContacts"
                        @complete="searchContacts($event)" :dropdown="true" optionLabel="label" forceSelection />
                    <label>Connection Name</label>
                </span>
            </div>

            <Button type="submit" label="Create" class="mt-5" :disabled="loading" :loading="loading" /> {{ loading }}
        </form>
    </div>
</template>

<script setup lang="ts">
// Vue
import { computed, reactive, ref } from "vue";

// PrimeVue / Validation
import AutoComplete from 'primevue/autocomplete';
import Button from "primevue/button";
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
    loading: ctLoad, credentialTemplateDropdown
} = storeToRefs(useGovernanceStore());
const loading = computed(() => cLoad.value || ctLoad.value)

// Form and Validation
const filteredCreds = ref();
const filteredContacts = ref();
const formFields = reactive({
    selectedContact: '',
    selectedCred: ''
});
const rules = {
    selectedCred: { required },
    selectedContact: { required }
}
const v$ = useVuelidate(rules, formFields)

// These can probably be generalized into a util function (for all dropdown searches)
const searchContacts = (event) => {
    if (!event.query.trim().length) {
        filteredContacts.value = [...contactsDropdown.value];
    }
    else {
        filteredContacts.value = contactsDropdown.value.filter((contact) => {
            return contact.label.toLowerCase().includes(event.query.toLowerCase());
        });
    };
};
const searchCreds = (event) => {
    if (!event.query.trim().length) {
        filteredCreds.value = [...credentialTemplateDropdown.value];
    }
    else {
        filteredCreds.value = credentialTemplateDropdown.value.filter((cred) => {
            return cred.label.toLowerCase().includes(event.query.toLowerCase());
        });
    };
};

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
    submitted.value = true;

    if (!isFormValid) {
        return;
    }

    let rrs = 0;
    try {
        rrs = parseInt(formFields.creddef_revocation_registry_size) || 0;
    } catch (err) {

    }
    const payload = {
        credential_definition: {
            tag: formFields.creddef_tag,
            revocation_enabled: formFields.creddef_revocation_enabled,
            revocation_registry_size: rrs
        },
        name: formFields.name,
        tags: []
    }

    console.log(payload);

    try {
        // call store
        await governanceStore.createCredentialTemplate(payload);
        toast.info('Credential Template Created');
    } catch (error) {
        toast.error(`Failure: ${error}`);
    } finally {
        submitted.value = false
    }
}
</script>