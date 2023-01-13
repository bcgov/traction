<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Invitation URL -->
    <div class="field">
      <label
        for="inviteUrl"
        :class="{ 'p-error': v$.inviteUrl.$invalid && submitted }"
      >
        Invitation Url
      </label>
      <Textarea
        id="inviteUrl"
        v-model="v$.inviteUrl.$model"
        :class="{ 'p-invalid': v$.inviteUrl.$invalid && submitted }"
        :auto-resize="true"
        rows="1"
        cols="75"
      />
      <span v-if="v$.inviteUrl.$error && submitted">
        <span v-for="(error, index) of v$.inviteUrl.$errors" :key="index">
          <small class="p-error block">{{ error.$message }}</small>
        </span>
      </span>
      <small v-else-if="v$.inviteUrl.$invalid && submitted" class="p-error">{{
        v$.inviteUrl.required.$message
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
          <small class="p-error">{{ error.$message }}</small>
        </span>
      </span>
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

// Validation
const formFields = reactive({
  inviteUrl: '',
  alias: '',
});
const rules = {
  inviteUrl: { required, url },
  alias: { maxLengthValue: maxLength(255) },
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
    // await contactsStore.acceptInvitation(
    //   formFields.inviteUrl,
    //   formFields.alias
    // );
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
