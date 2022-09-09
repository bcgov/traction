<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Alias -->
    <div class="field">
      <label for="alias" :class="{ 'p-error': v$.alias.$invalid && submitted }"
        >Contact Alias
      </label>
      <InputText
        v-model="v$.alias.$model"
        :class="{ 'p-invalid': v$.alias.$invalid && submitted }"
        type="text"
        name="alias"
        autofocus
        :readonly="!!invitation_url"
      />
      <small v-if="v$.alias.$invalid && submitted" class="p-error"
        >{{ v$.alias.required.$message }}
      </small>
    </div>

    <div v-if="invitation_url">
      <!-- QR Code Display -->
      <QRCode :qr-content="invitation_url" />

      <Button label="Close" class="mt-5 w-full" @click="$emit('closed')" />
    </div>
    <Button v-else type="submit" label="Submit" class="mt-5 w-full" />
  </form>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// State
import { useContactsStore } from '../../../store';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
// Other Components
import QRCode from '../../common/QRCode.vue';

const contactsStore = useContactsStore();

// For notifications
const toast = useToast();

// To store local data
const invitation_url = ref('');

// ----------------------------------------------------------------
// Creating a new contact
// ----------------------------------------------------------------
const emit = defineEmits(['closed', 'success']);

// Validation
const formFields = reactive({
  alias: '',
});
const rules = {
  alias: { required },
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
    // call store
    const result = await contactsStore.createInvitation(formFields.alias);
    if (result != null && result['invitation_url']) {
      invitation_url.value = result['invitation_url'];
      console.log(`invitation_url: ${invitation_url.value}`);
      toast.info('Contact Created');
      emit('success');
    }
    return false;
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};

// ---------------------------------------------------/create contact
</script>
