<template>
    <h3 class="mt-0 mb-5">Accept Invitation</h3>
    <div class="form-demo">
        <form @submit.prevent="handleSubmit(!v$.$invalid)">
            <div class="field">
                <div class="p-float-label">
                    <Textarea id="inviteUrl" v-model="v$.inviteUrl.$model"
                        :class="{ 'p-invalid': v$.inviteUrl.$invalid && submitted }" :autoResize="true" rows="1"
                        cols="100" />
                    <label for="inviteUrl" :class="{ 'p-error': v$.inviteUrl.$invalid && submitted }">Invitation
                        Url*</label>
                </div>
                <small v-if="v$.inviteUrl.$invalid && submitted" class="p-error">{{
                        v$.inviteUrl.required.$message.replace('Value', 'Invitation URL')
                }}</small>
            </div>
            <Button type="submit" label="Accept" class="mt-1" />
        </form>
    </div>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';

// PrimeVue
import Button from "primevue/button";
import Textarea from 'primevue/textarea';

// Other imports
import { required } from "@vuelidate/validators";
import { useVuelidate } from "@vuelidate/core";
import { useToast } from 'vue-toastification';

const toast = useToast();

// ----------------------------------------------------------------
// Accept Invite form
// ----------------------------------------------------------------
// Validation
const formFields = reactive({
    inviteUrl: ''
})
const rules = {
    inviteUrl: { required }
}
const v$ = useVuelidate(rules, formFields)

// Form submission
const submitted = ref(false);
const handleSubmit = (isFormValid: boolean) => {
    submitted.value = true;

    if (!isFormValid) {
        return;
    }

    alert('form sub');
}
// ---------------------------------------------------/accept form
</script>