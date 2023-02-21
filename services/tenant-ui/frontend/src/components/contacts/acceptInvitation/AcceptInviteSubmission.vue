<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Invitation URL -->
    <div class="field">
      <label
        for="invitationJson"
        :class="{ 'p-error': v$.invitationJson.$invalid && submitted }"
      >
        Invitation
      </label>
      <Textarea
        id="invitationJson"
        v-model="v$.invitationJson.$model"
        class="w-full"
        :class="{ 'p-invalid': v$.invitationJson.$invalid && submitted }"
        :auto-resize="true"
        rows="6"
      />
      <small v-if="v$.invitationJson.$invalid && submitted" class="p-error">{{
        v$.invitationJson.required.$message
      }}</small>
    </div>

    <!-- Alias -->
    <div class="field">
      <label for="alias" :class="{ 'p-error': v$.alias.$invalid && submitted }">
        Alias
      </label>
      <InputText
        id="alias"
        v-model="v$.alias.$model"
        class="w-full"
        :class="{ 'p-invalid': v$.alias.$invalid && submitted }"
      />
      <span v-if="v$.alias.$error && submitted">
        <span v-for="(error, index) of v$.alias.$errors" :key="index">
          <small class="p-error block">{{ error.$message }}</small>
        </span>
      </span>
      <small v-else-if="v$.alias.$invalid && submitted" class="p-error">{{
        v$.alias.required.$message
      }}</small>
    </div>
    <Button
      type="submit"
      label="Accept"
      class="mt-5 w-full"
      :disabled="loading"
      :loading="loading"
    />
  </form>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// State
import { useContactsStore } from '@/store';
import { storeToRefs } from 'pinia';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import { maxLength, required, url } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';

const toast = useToast();
const contactsStore = useContactsStore();

// use the loading state from the store to disable the button...
const { loading } = storeToRefs(useContactsStore());

const emit = defineEmits(['closed', 'success']);

const props = defineProps({
  invitationString: {
    type: String,
    default: '{}',
  },
});

// Validation
const formFields = reactive({
  invitationJson: props.invitationString,
  alias: '',
});
const rules = {
  invitationJson: { required },
  alias: { required, maxLengthValue: maxLength(255) },
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
    await contactsStore.recieveInvitation(
      formFields.invitationJson,
      formFields.alias
    );
    emit('success');
    // close up on success
    emit('closed');
    toast.info('Invitation Accepted');
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>
