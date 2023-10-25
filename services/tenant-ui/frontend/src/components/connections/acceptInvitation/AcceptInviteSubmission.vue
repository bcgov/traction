<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Invitation URL -->
    <div class="field">
      <label
        for="invitationJson"
        :class="{ 'p-error': v$.invitationJson.$invalid && submitted }"
      >
        {{ $t('connect.acceptInvitation.invitation') }}
      </label>
      <Textarea
        id="invitationJson"
        v-model="v$.invitationJson.$model"
        class="w-full"
        :class="{ 'p-invalid': v$.invitationJson.$invalid && submitted }"
        :auto-resize="true"
        rows="6"
      />
      <span v-if="v$.invitationJson.$error && submitted">
        <span v-for="(error, index) of v$.invitationJson.$errors" :key="index">
          <small class="p-error block">{{ error.$message }}</small>
        </span>
      </span>
    </div>

    <!-- Alias -->
    <div class="field">
      <label for="alias" :class="{ 'p-error': v$.alias.$invalid && submitted }">
        {{ $t('common.alias') }}
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
      :label="$t('common.submit')"
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
import { useConnectionStore } from '@/store';
import { storeToRefs } from 'pinia';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import { maxLength, required, helpers } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
// Other
import { isJsonString } from '@/helpers';

const toast = useToast();
const connectionStore = useConnectionStore();

// use the loading state from the store to disable the button...
const { loading } = storeToRefs(useConnectionStore());

const emit = defineEmits(['closed', 'success']);

const props = withDefaults(
  defineProps<{
    invitationString?: string;
    isOob?: boolean;
  }>(),
  {
    invitationString: '{}',
    isOob: false,
  }
);

// Validation
const formFields = reactive({
  invitationJson: props.invitationString,
  alias: '',
});
const rules = {
  invitationJson: {
    isJsonString: helpers.withMessage('Invalid JSON format', isJsonString),
  },
  alias: { required, maxLengthValue: maxLength(255) },
};
const v$ = useVuelidate(rules, formFields);

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;
  // Since the JSON field is set without user entry, to display custom error set the dirty flag
  v$.value.$touch();

  if (!isFormValid) {
    return;
  }

  try {
    await connectionStore.receiveInvitation(
      formFields.invitationJson,
      formFields.alias,
      props.isOob
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
